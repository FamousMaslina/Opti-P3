"""OPFS: persistent virtual drives with DOS-style paths.

O: maps to the working directory. Single-letter folders are separate drives;
host paths remain an internal detail of the virtual path interface.
"""
import json
import re
from pathlib import Path


class OPFS:
    def __init__(self, storage, working_directory=None):
        self._storage = Path(storage).resolve()
        self._working_directory = Path(working_directory or self._storage.parent).resolve()
        self.drives = {}
        self.current = 'O:/'

    def load(self):
        self._storage.mkdir(parents=True, exist_ok=True)
        manifest = self._storage / 'drives.json'
        if manifest.exists():
            self.drives = json.loads(manifest.read_text(encoding='utf-8'))
            for letter, drive in self.drives.items():
                self._letter(letter)
                if drive['kind'] not in ('system', 'hdd', 'floppy'):
                    raise ValueError('Invalid OPFS drive type')
                self._root(letter).mkdir(exist_ok=True)
        if 'O' not in self.drives:
            self.add_drive('O', 'system', 'Opti P3')
        # Existing letter folders are disks, even without motherboard entries.
        for folder in self._working_directory.iterdir():
            if folder.is_dir() and re.fullmatch('[A-Za-z]', folder.name):
                letter = folder.name.upper()
                if letter != 'O' and letter not in self.drives:
                    self.add_drive(letter, 'hdd', letter)
                    self.drives[letter]['discovered'] = True
        self._save()

    @staticmethod
    def _letter(letter):
        letter = letter.upper().rstrip(':')
        if not re.fullmatch('[A-Z]', letter):
            raise ValueError('Drive letters must be A-Z')
        return letter

    def _save(self):
        temporary = self._storage / 'drives.tmp'
        temporary.write_text(json.dumps(self.drives, indent=2), encoding='utf-8')
        temporary.replace(self._storage / 'drives.json')

    def _root(self, letter):
        letter = self._letter(letter)
        if letter == 'O':
            return self._working_directory
        root = self._working_directory / letter
        if not root.exists():
            # Match lower-case drive folders on case-sensitive hosts too.
            root = next((p for p in self._working_directory.iterdir()
                         if p.name.upper() == letter and p.is_dir()), root)
        base = self._working_directory
        legacy = self._storage / letter
        if not root.exists() and legacy.exists():
            root, base = legacy, self._storage
        if root.is_symlink() or root.resolve().parent != base:
            raise ValueError('Invalid OPFS storage')
        return root

    def add_drive(self, letter, kind='hdd', label='', device=None):
        letter = self._letter(letter)
        if letter in self.drives:
            raise ValueError(f'Drive {letter}: already exists')
        if kind not in ('system', 'hdd', 'floppy'):
            raise ValueError('Drive type must be hdd or floppy')
        self._root(letter).mkdir(exist_ok=True)
        self.drives[letter] = dict(kind=kind, label=label or letter, device=device)
        self._save()
        return letter

    def mount_device(self, device, kind, label, letter=None):
        for existing, info in self.drives.items():
            if info.get('device') == device:
                return existing
        if letter:
            letter = self._letter(letter)
            if letter in self.drives and self.drives[letter].get('discovered'):
                self.drives[letter].update(kind=kind, label=label, device=device, discovered=False)
                self._save()
                return letter
            return self.add_drive(letter, kind, label, device)
        preferred = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if kind == 'floppy' else 'CDEFGHIJKLMNOPQRSTUVWXYZAB'
        for candidate in preferred:
            if candidate in self.drives and self.drives[candidate].get('discovered'):
                self.drives[candidate].update(kind=kind, label=label, device=device, discovered=False)
                self._save()
                return candidate
            if candidate not in self.drives:
                return self.add_drive(candidate, kind, label, device)
        raise ValueError('All OPFS drive letters are in use')

    def resolve(self, path='.'):
        path = str(path).replace('\\', '/')
        if '\x00' in path or path.startswith('//'):
            raise ValueError('Invalid OPFS path')
        current_letter, current_path = self.current.split(':', 1)
        match = re.match(r'^([A-Za-z]):(.*)$', path)
        if match:
            letter, path = match.group(1).upper(), match.group(2)
            parts = []
        else:
            letter = current_letter
            parts = [] if path.startswith('/') else current_path.strip('/').split('/')
        if letter not in self.drives:
            raise ValueError(f'Drive {letter}: not found')
        for part in path.split('/'):
            if part in ('', '.'):
                continue
            if part == '..':
                if parts:
                    parts.pop()
                continue
            # Reject host device paths, alternate streams, and Windows aliases.
            if any(c in part for c in ':<>"|?*') or part.endswith((' ', '.')):
                raise ValueError('Invalid OPFS filename')
            if re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part, re.I):
                raise ValueError('Invalid OPFS filename')
            parts.append(part)
        return letter + ':/' + '/'.join(p for p in parts if p)

    def host_path(self, path='.'):
        virtual = self.resolve(path)
        letter, relative = virtual.split(':/', 1)
        root = self._root(letter)
        first = relative.split('/', 1)[0]
        if letter == 'O' and first:
            entry = root / first
            if entry == self._storage:
                raise ValueError('OPFS metadata is not a virtual directory')
            if re.fullmatch('[A-Za-z]', first) and entry.is_dir():
                raise ValueError(f'Use {first.upper()}: to access this drive')
        target = root
        for part in relative.split('/'):
            if part:
                if self._hidden_name(part):
                    raise ValueError('Path is hidden from OPFS')
                target = target / part
                if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
                    raise ValueError('OPFS links outside a drive are not allowed')
        return target

    @staticmethod
    def _hidden_name(name):
        name = name.casefold()
        return name.startswith('.git') or name in ('__pycache__', 'pycache')

    def chdir(self, path):
        virtual = self.resolve(path)
        if not self.host_path(virtual).is_dir():
            raise ValueError(f'Directory not found: {virtual}')
        self.current = virtual

    def listdir(self):
        entries = []
        for child in self.host_path().iterdir():
            if self._hidden_name(child.name):
                continue
            if self.current == 'O:/' and (
                    child == self._storage or
                    (child.is_dir() and re.fullmatch('[A-Za-z]', child.name))):
                continue
            try:
                safe = self.host_path(child.name)
            except ValueError:
                continue
            entries.append((child.name, safe.is_dir(), safe.stat().st_size))
        return sorted(entries, key=lambda item: (not item[1], item[0].lower()))

    def mkdir(self, path):
        self.host_path(path).mkdir(parents=True, exist_ok=True)

    def touch(self, path):
        self.host_path(path).touch(exist_ok=True)

    def remove(self, path, directory=False):
        virtual = self.resolve(path)
        if virtual.endswith(':/'):
            raise ValueError('Cannot remove a drive root')
        if directory and (self.current == virtual or self.current.startswith(virtual + '/')):
            raise ValueError('Cannot remove the current directory')
        target = self.host_path(virtual)
        if directory:
            target.rmdir()
        else:
            target.unlink()
