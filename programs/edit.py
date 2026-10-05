"""A small Nano-style terminal editor for OPFS, without extra dependencies."""
import contextlib
import os
from pathlib import Path
import shutil
import sys


class Buffer:
    def __init__(self, text=''):
        self.lines = text.split('\n')
        self.row = self.column = 0
        self.dirty = False
        self.clipboard = ''

    def insert(self, text):
        line = self.lines[self.row]
        pieces = (line[:self.column] + text + line[self.column:]).split('\n')
        self.lines[self.row:self.row + 1] = pieces
        if '\n' in text:
            self.row += text.count('\n')
            self.column = len(text.rsplit('\n', 1)[-1])
        else:
            self.column += len(text)
        self.dirty = True

    def backspace(self):
        if self.column:
            line = self.lines[self.row]
            self.lines[self.row] = line[:self.column - 1] + line[self.column:]
            self.column -= 1
        elif self.row:
            tail = self.lines.pop(self.row)
            self.row -= 1
            self.column = len(self.lines[self.row])
            self.lines[self.row] += tail
        else:
            return
        self.dirty = True

    def delete(self):
        line = self.lines[self.row]
        if self.column < len(line):
            self.lines[self.row] = line[:self.column] + line[self.column + 1:]
        elif self.row + 1 < len(self.lines):
            self.lines[self.row] += self.lines.pop(self.row + 1)
        else:
            return
        self.dirty = True

    def move(self, key, page=10):
        if key == 'LEFT':
            if self.column:
                self.column -= 1
            elif self.row:
                self.row -= 1
                self.column = len(self.lines[self.row])
        elif key == 'RIGHT':
            if self.column < len(self.lines[self.row]):
                self.column += 1
            elif self.row + 1 < len(self.lines):
                self.row += 1
                self.column = 0
        elif key in ('UP', 'DOWN', 'PAGEUP', 'PAGEDOWN'):
            delta = {'UP': -1, 'DOWN': 1, 'PAGEUP': -page, 'PAGEDOWN': page}[key]
            self.row = min(max(0, self.row + delta), len(self.lines) - 1)
            self.column = min(self.column, len(self.lines[self.row]))
        elif key == 'HOME':
            self.column = 0
        elif key == 'END':
            self.column = len(self.lines[self.row])

    def cut(self):
        self.clipboard = self.lines.pop(self.row) + '\n'
        if not self.lines:
            self.lines = ['']
        self.row = min(self.row, len(self.lines) - 1)
        self.column = 0
        self.dirty = True

    def find(self, query):
        if not query:
            return False
        # Search after the cursor, then wrap around to the beginning.
        positions = [(self.row, self.column + 1)]
        positions += [(row, 0) for row in range(self.row + 1, len(self.lines))]
        positions += [(row, 0) for row in range(self.row + 1)]
        for row, start in positions:
            column = self.lines[row].find(query, start)
            if column >= 0:
                self.row, self.column = row, column
                return True
        return False


class Terminal:
    @contextlib.contextmanager
    def session(self):
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError('edit requires an interactive terminal')
        if os.name == 'nt':
            import ctypes
            from ctypes import wintypes
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel.GetStdHandle.argtypes = [wintypes.DWORD]
            kernel.GetStdHandle.restype = wintypes.HANDLE
            kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            handle = kernel.GetStdHandle(-11)
            mode = wintypes.DWORD()
            if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
                raise ValueError('Cannot access the terminal console')
            if not kernel.SetConsoleMode(handle, mode.value | 0x0004):
                raise ValueError('Terminal does not support ANSI display')
            restore = lambda: kernel.SetConsoleMode(handle, mode.value)
        else:
            import termios
            import tty
            descriptor = sys.stdin.fileno()
            old = termios.tcgetattr(descriptor)
            tty.setraw(descriptor)
            restore = lambda: termios.tcsetattr(descriptor, termios.TCSADRAIN, old)
        try:
            self.write('\x1b[?1049h\x1b[?25h')
            yield
        finally:
            self.write('\x1b[?25h\x1b[?1049l')
            restore()

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def key(self):
        if os.name == 'nt':
            import msvcrt
            try:
                key = msvcrt.getwch()
            except KeyboardInterrupt:
                return '\x03'
            if key in ('\x00', '\xe0'):
                return {'H': 'UP', 'P': 'DOWN', 'K': 'LEFT', 'M': 'RIGHT',
                        'G': 'HOME', 'O': 'END', 'S': 'DELETE',
                        'I': 'PAGEUP', 'Q': 'PAGEDOWN'}.get(msvcrt.getwch(), '')
            return key
        import select
        descriptor = sys.stdin.fileno()
        raw = os.read(descriptor, 1)
        while raw and raw[0] >= 0xc0:
            try:
                raw.decode('utf-8')
                break
            except UnicodeDecodeError:
                if len(raw) >= 4:
                    break
                raw += os.read(descriptor, 1)
        key = raw.decode('utf-8', errors='replace')
        if key != '\x1b':
            return key
        sequence = ''
        while select.select([descriptor], [], [], 0.04)[0]:
            sequence += os.read(descriptor, 1).decode('ascii', errors='replace')
            if sequence[-1].isalpha() or sequence[-1] == '~':
                break
        return {'[A': 'UP', '[B': 'DOWN', '[C': 'RIGHT', '[D': 'LEFT',
                '[H': 'HOME', '[F': 'END', 'OH': 'HOME', 'OF': 'END',
                '[1~': 'HOME', '[4~': 'END', '[3~': 'DELETE',
                '[5~': 'PAGEUP', '[6~': 'PAGEDOWN'}.get(sequence, '\x1b')


def display_text(text):
    # File contents must not inject terminal control sequences.
    return ''.join(character if character.isprintable() else ' ' for character in text)


class Editor:
    def __init__(self, filesystem, filename=None, terminal=None):
        self.filesystem = filesystem
        self.filename = filesystem.resolve(filename) if filename else None
        self.terminal = terminal or Terminal()
        self.newline = '\n'
        self.encoding = 'utf-8'
        text = ''
        if self.filename:
            path = filesystem.host_path(self.filename)
            if path.exists():
                raw = path.read_bytes()
                if b'\x00' in raw:
                    raise ValueError('edit supports text files only')
                self.encoding = 'utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8'
                self.newline = '\r\n' if b'\r\n' in raw else '\n'
                text = raw.decode(self.encoding).replace('\r\n', '\n')
        self.buffer = Buffer(text)
        self.top = self.left = 0
        self.message = 'New file' if not text else 'File loaded'

    def render(self, prompt=None):
        width, height = shutil.get_terminal_size((80, 24))
        width, height = max(1, width), max(5, height)
        rows = height - 4
        buffer = self.buffer
        self.top = min(self.top, buffer.row)
        if buffer.row >= self.top + rows:
            self.top = buffer.row - rows + 1
        self.left = min(self.left, buffer.column)
        if buffer.column >= self.left + width:
            self.left = buffer.column - width + 1
        title = f" OP3 edit  |  {self.filename or '[New Buffer]'}{'  * Modified' if buffer.dirty else ''}"
        screen = ['\x1b[H\x1b[7m' + display_text(title)[:width].ljust(width) + '\x1b[0m']
        for index in range(rows):
            line = buffer.lines[self.top + index] if self.top + index < len(buffer.lines) else ''
            screen.append(f'\x1b[{index + 2};1H\x1b[2K' + display_text(line)[self.left:self.left + width])
        status = prompt if prompt is not None else f'{self.message}  |  Ln {buffer.row + 1}, Col {buffer.column + 1}'
        for row, text in ((height - 2, status),
                          (height - 1, '^G Help  ^O Write Out  ^W Search  ^K Cut Line'),
                          (height, '^X Exit  ^S Save       ^U Paste   Arrows Move')):
            screen.append(f'\x1b[{row};1H\x1b[2K' + display_text(text)[:max(0, width - 1)])
        if prompt is not None:
            screen.append(f'\x1b[{height - 2};{min(len(display_text(prompt)) + 1, width)}H')
        else:
            screen.append(f'\x1b[{buffer.row - self.top + 2};{buffer.column - self.left + 1}H')
        self.terminal.write(''.join(screen))

    def ask(self, label, initial=''):
        answer = initial
        while True:
            self.render(label + answer)
            key = self.terminal.key()
            if key in ('\r', '\n'):
                return answer
            if key in ('\x1b', '\x03', '\x18'):
                return None
            if key in ('\b', '\x7f'):
                answer = answer[:-1]
            elif len(key) == 1 and key.isprintable():
                answer += key

    def save(self, filename):
        virtual = self.filesystem.resolve(filename)
        path = self.filesystem.host_path(virtual)
        text = '\n'.join(self.buffer.lines).replace('\n', self.newline)
        path.write_bytes(text.encode(self.encoding))
        self.filename = virtual
        self.buffer.dirty = False
        self.message = f'Saved {len(self.buffer.lines)} lines'

    def write_out(self, prompt=True):
        filename = self.ask('File Name to Write: ', self.filename or '') if prompt or not self.filename else self.filename
        if not filename:
            self.message = 'Save cancelled'
            return False
        try:
            self.save(filename)
            return True
        except (OSError, ValueError) as error:
            self.message = 'Save failed: ' + (error.strerror if isinstance(error, OSError) else str(error))
            return False

    def run(self):
        with self.terminal.session():
            while True:
                self.render()
                key = self.terminal.key()
                if key == '\x18':
                    if not self.buffer.dirty:
                        return
                    answer = self.ask('Save changes? Y/N (Esc cancels): ')
                    if answer and answer.lower() == 'n':
                        return
                    if answer and answer.lower() == 'y' and self.write_out():
                        return
                elif key in ('\x0f', '\x13'):
                    self.write_out(prompt=key == '\x0f')
                elif key == '\x17':
                    query = self.ask('Search: ')
                    if query:
                        self.message = 'Found' if self.buffer.find(query) else 'Not found'
                elif key == '\x0b':
                    self.buffer.cut()
                elif key == '\x15':
                    if self.buffer.clipboard:
                        self.buffer.insert(self.buffer.clipboard)
                elif key == '\x07':
                    self.message = 'Ctrl+O save as; Ctrl+S save; Ctrl+X exit; prompts: Enter accepts, Esc cancels'
                elif key == '\x03':
                    self.message = 'Use Ctrl+X to exit; Ctrl+S to save'
                elif key in ('\b', '\x7f'):
                    self.buffer.backspace()
                elif key == 'DELETE':
                    self.buffer.delete()
                elif key in ('\r', '\n'):
                    self.buffer.insert('\n')
                elif key == '\t':
                    self.buffer.insert('    ')
                elif key in ('UP', 'DOWN', 'LEFT', 'RIGHT', 'HOME', 'END', 'PAGEUP', 'PAGEDOWN'):
                    self.buffer.move(key, max(1, shutil.get_terminal_size().lines - 4))
                elif len(key) == 1 and key.isprintable():
                    self.buffer.insert(key)


def edit_file(filesystem, filename=None):
    try:
        Editor(filesystem, filename).run()
    except KeyboardInterrupt:
        print('Editor interrupted; unsaved changes were discarded.')
    except (OSError, ValueError) as error:
        print('edit: ' + (error.strerror if isinstance(error, OSError) else str(error)))


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from op3 import filesystem
    filesystem.load()
    edit_file(filesystem, ' '.join(sys.argv[1:]) or None)
