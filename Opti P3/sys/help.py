import os
import sys

def clear():
    """Clear screen compatible with Windows and Unix"""
    os.system('cls' if os.name == 'nt' else 'clear')

def linebr(length=40):
    """Draw a line of characters"""
    print("=" * length)

def linebr2(length=40):
    """Draw a dashed line"""
    print("-" * length)

def show_help(page=1):
    """Display help with paging support"""
    help_pages = [
        # Page 1 - Basic Commands
        """\
OP3 Help System - Page 1/3
==========================

Basic Commands:
--------------
help [page]    - Show this help (specify page number)
cls/clear      - Clear the screen
info           - Show system information
exit           - Exit OP3
reboot         - Restart the system
shutdown       - Shut down the system

File Operations:
---------------
dir/ls         - List directory contents
cd <dir>       - Change directory
mkdir <dir>    - Create directory
rmdir <dir>    - Remove empty directory
del <file>     - Delete file (aliases: delete, rm)
touch <file>   - Create empty file
run <program>  - Run a Python program

Press Enter for next page...""",

        # Page 2 - System Management
        """\
OP3 Help System - Page 2/3
==========================

System Management:
-----------------
computername   - Change computer name
autostart      - Manage startup programs
config         - Configuration editor
settings       - Alias for config
manage_extensions - Manage plugins

Hardware Info:
-------------
bios           - Enter BIOS setup
dvcman         - Show hardware information
hdinfo         - Display hard drive details

Press Enter for next page...""",

        # Page 3 - Advanced
        """\
OP3 Help System - Page 3/3
==========================

Advanced Commands:
----------------
root           - Return to root directory
create-template - Create program template

Plugins:
-------
Most plugins add their own commands. Use 
'manage_extensions' to see available plugins.

"""
    ]

    try:
        page = int(page) if str(page).isdigit() else 1
        if page < 1 or page > len(help_pages):
            page = 1
    except ValueError:
        page = 1

    clear()
    print(help_pages[page-1])

    if page < len(help_pages):
        input()
        show_help(page + 1)
    else:
        input("\nPress Enter to return to OP3...")

if __name__ == "__main__":
    show_help(sys.argv[1] if len(sys.argv) > 1 else 1)