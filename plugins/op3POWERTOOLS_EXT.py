import os
import subprocess
import sys
import psutil
from configparser import ConfigParser
from pathlib import Path

# Import from op3.py
import op3
from op3 import op3vIST, op3vIINT

VERSION = '1.0.4'
BASE_DIRECTORY = Path(__file__).resolve().parent.parent

def linebr(number):
    print("=" * number)

def linebr2(number):
    print("-" * number)

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def is_script_running(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any(script_name in arg for arg in cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def _set_debug_mode(enabled):
    # Running op3.py creates __main__; importing op3 creates a separate module.
    # Update the manager used by the running shell, whichever module owns it.
    main_module = sys.modules.get('__main__')
    runtime = (main_module if getattr(main_module, 'hw_manager', None) is not None
               and Path(getattr(main_module, '__file__', '')).resolve() == BASE_DIRECTORY / 'op3.py'
               else op3)
    manager = getattr(runtime, 'hw_manager', None)
    config_path = Path(manager.config_file) if manager else Path('sys/ini/op3.ini')
    if not config_path.is_absolute():
        config_path = BASE_DIRECTORY / config_path
    config = ConfigParser()
    config.read(config_path)
    if not config.has_section('user'):
        config.add_section('user')
    value = '1' if enabled else '0'
    config.set('user', 'debug_mode', value)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open('w') as config_file:
        config.write(config_file)
    if manager:
        if not manager.config.has_section('user'):
            manager.config.add_section('user')
        manager.config.set('user', 'debug_mode', value)
    print(f"DEBUG MODE {'ENABLED' if enabled else 'DISABLED'}")

def enable_debug_mode():
    _set_debug_mode(True)

def disable_debug_mode():
    _set_debug_mode(False)

def run_opfs_tests():
    tests_directory = BASE_DIRECTORY / 'tests'
    if not (tests_directory / 'test_opfs.py').is_file():
        print('OPFS tests are unavailable: local tests/test_opfs.py is missing.')
        return False
    result = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', str(tests_directory),
         '-p', 'test_opfs.py', '-v'], cwd=str(BASE_DIRECTORY))
    print('OPFS tests passed.' if result.returncode == 0 else 'OPFS tests failed.')
    return result.returncode == 0

def delete_autostart():
    autostart_path = BASE_DIRECTORY / 'sys' / 'autostart.txt'
    if os.path.exists(autostart_path):
        os.remove(autostart_path)
        print("Deleted autostart.txt")
    else:
        print("No autostart.txt file found.")

def delete_id_files():
    files = [
        BASE_DIRECTORY / 'hw' / name
        for name in ('idcpu.py', 'idmb.py', 'idmon.py', 'idkey.py', 'idhd.py')
    ]
    for filename in files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted {filename}")
        else:
            print(f"{filename} not found.")

def show_version_info():
    clear()
    print("OP3 Power Tools EXT", VERSION)
    linebr(40)
    print("1. Enable DEBUG mode")
    print("2. Disable DEBUG mode")
    print("3. Delete or Reset AUTOSTART")
    print("4. Delete ID Files")
    print("5. Return to OP3")
    print("6. Run OPFS tests")
    linebr2(40)
    print("OP3 Reported Version:", op3vIST)
    print("OP3 Reported Integer Version:", op3vIINT)
    script_name = "op3.py"
    if is_script_running(script_name):
        print(f"{script_name} is running.")
    else:
        print(f"{script_name} is not running.")
    linebr(40)

def manage_power_tools():
    show_version_info()
    while True:
        a = input("Enter choice: ").strip()
        if a == "1":
            enable_debug_mode()
        elif a == "2":
            disable_debug_mode()
        elif a == "3":
            delete_autostart()
        elif a == "4":
            delete_id_files()
        elif a == "5":
            break
        elif a == "6":
            run_opfs_tests()
        else:
            clear()
            print("Unknown choice. Please try again.")
            show_version_info()

commands = {
    'manage_tools': manage_power_tools,
    'powertools': manage_power_tools,
    'test_opfs': run_opfs_tests
}

info = {
    'title': 'OP3 Power Tools',
    'version': VERSION,
    'author': 'FamousMaslina',
    'description': 'Manage various OP3 settings quicker.',
    'commands': ', '.join(commands.keys())
}
