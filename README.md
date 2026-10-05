# Opti P3 - The Sequel to OP2
Inspired by MS-DOS

Current version: **0.2.0** (integer version: `0.2`).

## Why this?
* I want more things to do this summer. (and C++ too :)). 

## Instructions:
### For Windows:
* Download from releases tab, extract it, then run op3.py.

### For Linux:
* (Linux Support & Tutorial coming in N/A)

## Update log 0.2.0:

* Added OPFS virtual drive letters, multiple disks, and working-directory access.
* Added the Nano-style `edit` text editor with OPFS support.
* Updated PowerTools to 1.0.4 with working debug controls and a local OPFS test runner.
* Added Git ignore rules for local tests, virtual disk metadata, and Python caches.

## Update log 0.1.5:
* Added 'dvcman' (fix #9)
* Added lots of CPUs ported from OP2
* Added OP2 app compatibility (BETA)

## OPFS virtual filesystem

OPFS gives the shell persistent drive letters and virtual paths. The system
drive `O:/` maps to the working directory where you launch OP3, so `dir` and
`ls` show folders such as `hw`, `plugins`, `sys`, and `programs`.
Single-letter drive folders (`A`, `B`, `C`, `O`, etc.) are hidden from the
system root listing. Existing letter folders are automatically mounted as
drives; access their contents with `A:`, `C:`, or `cd C:/documents`, rather
than `cd C`. `O:` is reserved for the working directory itself.
Git entries beginning with `.git` and `__pycache__`/`pycache` folders are
hidden from listings and direct OPFS access on every drive and in subfolders
(case insensitive). `README.md` files remain visible and accessible.
All enabled motherboard `portIDE*` and `portFDC*` entries get separate hard disk
or floppy drives. There is no four-floppy limit; up to 26 drive letters are
available, including the system drive. Drive contents and assignments survive
restarts.

Use `drives` or `opfs` to list disks. Add custom disks with
`opfs add X hdd Work` or `opfs add Y floppy Backup`. Switch with `X:` and use
paths such as `X:/documents` or `X:\documents`. Each hardware port may specify
`"drive_letter": "X"` to choose its letter on first mounting. Letters must be
unique; existing saved assignments take precedence on later boots.

`dir`, `cd`, `mkdir`, `touch`, `del`, `rmdir`, `root`, `create-template`, and
`run` use OPFS paths. Relative paths stay on the current drive; `/` returns to
its root, and `..` stops at that root. Paths with spaces are supported by file
commands. `touch` preserves existing file contents.

New disks store files in their letter folders in the working directory
(`A/`, `C/`, `X/`, etc.). Drive assignments are saved in `.opfs/drives.json`;
this metadata folder is hidden from the OPFS system listing. Existing disks
from the previous `.opfs/<letter>/` layout remain accessible when there is no
matching letter folder in the working directory. Files already in the working
directory can be used directly, for example `run programs/ex2.py`.
OPFS confines navigation to each drive and hides host paths in filesystem
errors. Python programs, BIOS tools, and plugins still run as normal host code.
## New issues identified:

## OP3 PowerTools 1.0.4

Run `powertools` or `manage_tools` to open the maintenance menu. Debug controls
update the real debug flag immediately and preserve the computer name.
Option 6 runs the local OPFS test suite; `test_opfs` runs it directly.
The `tests/` folder is ignored by Git, so this option requires a local
`tests/test_opfs.py` copy. When it is absent, PowerTools reports that tests
are unavailable.

## Text editor

Use `edit notes.txt` or `edit A:/notes.txt` to open a UTF-8 text file in the
Nano-style terminal editor in `programs/edit.py`. `edit` opens an unnamed
buffer. Arrow keys, Home/End, Page Up/Down, Backspace, and Delete navigate and
edit text. Ctrl+O writes a file (Enter confirms the filename), Ctrl+S saves,
Ctrl+W searches, Ctrl+K cuts a line, Ctrl+U pastes, and Ctrl+X exits with a
save prompt for modified text. Escape cancels prompts. Existing UTF-8 BOMs
and Windows line endings are preserved. Tabs typed in the editor insert
four spaces. Run it in an interactive Windows or Unix terminal.


