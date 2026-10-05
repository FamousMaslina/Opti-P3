import os
import random
import subprocess
import psutil
from configparser import ConfigParser

# Import from op3.py
from op3 import op3vIST, op3vIINT, HardwareManager

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

def enable_debug_mode():
    config = ConfigParser()
    config.read(os.path.join("sys", "ini", "op3.ini"))
    settings = config["user"]
    new = "DEBUG_MODE"
    settings['computer_name'] = new
    with open(os.path.join("sys", "ini", "op3.ini"), 'w') as a:
        config.write(a)
    print("DEBUG MODE ENABLED")

def disable_debug_mode():
    config = ConfigParser()
    config.read(os.path.join("sys", "ini", "op3.ini"))
    settings = config["user"]
    new = "DEFAULT"
    settings['computer_name'] = new
    with open(os.path.join("sys", "ini", "op3.ini"), 'w') as a:
        config.write(a)
    print("DEBUG MODE DISABLED")

def delete_autostart():
    autostart_path = os.path.join("sys", "autostart.txt")
    if os.path.exists(autostart_path):
        os.remove(autostart_path)
        print("Deleted autostart.txt")
    else:
        print("No autostart.txt file found.")

def delete_id_files():
    files = [
        os.path.join("hw", "idcpu.py"),
        os.path.join("hw", "idmb.py"),
        os.path.join("hw", "idmon.py"),
        os.path.join("hw", "idkey.py"),
        os.path.join("hw", "idhd.py")
    ]
    for filename in files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted {filename}")
        else:
            print(f"{filename} not found.")

def show_version_info():
    clear()
    ver = "1.0.3"  # Updated version for OP3
    print("OP3 Power Tools EXT", ver)
    linebr(40)
    print("1. Enable DEBUG mode")
    print("2. Disable DEBUG mode")
    print("3. Delete or Reset AUTOSTART")
    print("4. Delete ID Files")
    print("5. Return to OP3")
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
        else:
            clear()
            print("Unknown choice. Please try again.")
            show_version_info()

commands = {
    'manage_tools': manage_power_tools,
    'powertools': manage_power_tools  # Added alias for convenience
}

info = {
    'title': 'OP3 Power Tools',
    'version': '1.0.3',
    'author': 'FamousMaslina',
    'description': 'Manage various OP3 settings quicker.',
    'commands': ', '.join(commands.keys())
}