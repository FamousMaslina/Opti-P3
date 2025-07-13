import os
from os import name, system
import sys
import time
import configparser
from importlib import import_module

def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

# === Setup Paths ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
HW_DIR = os.path.join(PROJECT_ROOT, "hw")
SYS_DIR = os.path.join(PROJECT_ROOT, "sys")
INI_DIR = os.path.join(SYS_DIR, "ini")

# Add the hw directory to sys.path for module importing
if HW_DIR not in sys.path:
    sys.path.append(HW_DIR)

# === Fast Boot Configuration ===
def load_fastboot_setting():
    """Load fastboot setting from op3.ini"""
    config = configparser.ConfigParser()
    config_file = os.path.join(INI_DIR, "op3.ini")
    
    if os.path.exists(config_file):
        config.read(config_file)
        return config.getboolean('sys', 'fastboot', fallback=False)
    return False

# Apply fastboot setting globally
FASTBOOT = load_fastboot_setting()
BIOS_DELAY = 0.05 if FASTBOOT else 0.2

# === Clean ID Files ===
def clean_ids():
    id_files = ["idcpu.py", "idmb.py", "idhd.py", "idmon.py", "idkey.py"]
    for file in id_files:
        try:
            os.remove(os.path.join(HW_DIR, file))
        except FileNotFoundError:
            pass

clean_ids()
time.sleep(BIOS_DELAY)

# === BIOS Configuration ===
bios_name = "Phoenix 386 BIOS"
bios_version = "3.1.0"
required_mb_code = "386basic"

# === Hardware Detection ===
def detect_hardware():
    hw_types = [
        ("asdawd2k3a403", "idcpu.py", "cpu"),
        ("KSADFAS", "idmb.py", "mb"),
        ("hdd1name", "idhd.py", "hd"),
        ("mmmnni", "idmon.py", "mon"),
        ("kkeyb", "idkey.py", "key"),
        ("gpu_identifier", "idgpu.py", "gpu"),
        ("modem_identifier", "idmodem.py", "modem"),
        ("sound_identifier", "idsound.py", "sound")
    ]

    for identifier, id_file, var_name in hw_types:
        for file in os.listdir(HW_DIR):
            if file.endswith(".py") and file not in ["bios.py", "op3.py"]:
                with open(os.path.join(HW_DIR, file), "r") as f:
                    if identifier in f.read():
                        with open(os.path.join(HW_DIR, id_file), "w") as idf:
                            idf.write(f"{var_name} = '{file}'")

detect_hardware()
time.sleep(BIOS_DELAY)

# === Import ID Files ===
from idcpu import cpu
from idmb import mb
try:
    from idhd import hd
except ImportError:
    hd = None

from idmon import mon
from idkey import key

# === Load Hardware Modules ===
def load_module(file_var):
    return import_module(file_var.replace(".py", ""))

mb_module = load_module(mb)
cpu_module = load_module(cpu)
hd_module = load_module(hd) if hd else None
mon_module = load_module(mon)
key_module = load_module(key)

# Utility to capture input with a timeout for BIOS prompts
def timed_input(prompt, timeout):
    """Return user input if entered within timeout seconds, else None."""
    print(prompt, end='', flush=True)
    if os.name == 'nt':
        import msvcrt
        start = time.time()
        buf = ''
        while time.time() - start < timeout:
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                if char in ('\r', '\n'):
                    print()
                    return buf
                buf += char
            time.sleep(0.05)
        print()
        return None
    else:
        import select, sys
        sys.stdout.flush()
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        print()
        return None

# Helper to retrieve storage info from either dedicated HD module or
# motherboard IDE ports
def get_primary_storage():
    if hd_module and hasattr(hd_module, 'hddname'):
        size = getattr(hd_module, 'hddspace', None)
        if size:
            return f"{hd_module.hddname} ({size}KB)"
        return hd_module.hddname

    for attr in dir(mb_module):
        if attr.startswith('portIDE'):
            port = getattr(mb_module, attr)
            if isinstance(port, dict) and port.get('use', False):
                name = port.get('hdd1name') or port.get('hdd2name')
                size = port.get('hdd1storageSTR') or port.get('hdd2storageSTR')
                if name:
                    return f"{name} ({size})" if size else name
    return 'None'

# === BIOS/MB Compatibility Check ===
if not hasattr(mb_module, 'bcode') or mb_module.bcode != required_mb_code:
    print(f"{bios_name} ERROR: Incompatible motherboard!")
    print(f"Expected MB code: {required_mb_code}")
    print(f"Found MB code: {getattr(mb_module, 'bcode', 'None')}")
    while True:
        time.sleep(1)

# === System Info ===
def show_system_info():
    print(f"\n{bios_name} v{bios_version}")
    print("=========================")
    print(f"Motherboard: {getattr(mb_module, 'mbName', 'Unknown')}")
    print(f"CPU: {cpu_module.cName} @ {cpu_module.cFreqS}{cpu_module.cFreqUnit}")
    print(f"Memory: {getattr(mb_module, 'mbMemSTR', 'Unknown')}")
    print(f"Primary Storage: {get_primary_storage()}")
    print(f"Monitor: {getattr(mon_module, 'monitorName', 'Standard VGA')}")
    print(f"Fast Boot: {'Enabled' if FASTBOOT else 'Disabled'}")
    print("=========================\n")

# Allow user to enter BIOS shortly after POST
def check_bios_prompt():
    choice = timed_input("Press B to enter BIOS setup...", 2)
    if choice and choice.lower().startswith('b'):
        bios_menu()

# === CMOS Setup ===
def standard_cmos_setup():
    clear()
    print("\nStandard CMOS Setup")
    print("------------------")
    print(f"Date: {time.strftime('%m/%d/%Y')}")
    print(f"Time: {time.strftime('%H:%M:%S')}")
    print("\nDrive Configuration:")

    ide_devices = []

    for attr_name in dir(mb_module):
        if attr_name.startswith("portIDE"):
            port = getattr(mb_module, attr_name)
            if isinstance(port, dict) and port.get("use", False):
                name = next((v for k, v in port.items() if "name" in k.lower()), "IDE Device")
                size = next((v for k, v in port.items() if "storagestr" in k.lower()), "Unknown")
                ide_devices.append(f"{attr_name}: {name} ({size})")

    print("\n".join(ide_devices) if ide_devices else "No IDE devices detected")
    
    # Add Fast Boot toggle option
    print("\nFast Boot: [Enabled]" if FASTBOOT else "\nFast Boot: [Disabled]")
    print("Press F to toggle Fast Boot")
    
    choice = input("\nPress Enter to return or F to toggle Fast Boot: ").lower()
    if choice == 'f':
        toggle_fastboot()
    clear()

def toggle_fastboot():
    """Toggle fastboot setting in config"""
    config = configparser.ConfigParser()
    config_file = os.path.join(INI_DIR, "op3.ini")
    
    if not os.path.exists(config_file):
        print("Config file not found!")
        return
    
    config.read(config_file)
    current = config.getboolean('sys', 'fastboot', fallback=False)
    config.set('sys', 'fastboot', str(not current).lower())
    
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    
    print(f"\nFast Boot {'Enabled' if not current else 'Disabled'}")
    time.sleep(1)

# === BIOS Menu ===
def bios_menu():    
    while True:
        clear()
        show_system_info()
        print("Main BIOS Menu")
        print("1. Standard CMOS Setup")
        print("2. BIOS Features Setup")
        print("3. Chipset Features Setup")
        print("4. Power Management Setup")
        print("5. Load Setup Defaults")
        print("6. Save & Exit Setup")
        print("7. Toggle Fast Boot (Current: " + ("On" if FASTBOOT else "Off") + ")")

        choice = input("Enter choice: ")

        if choice == "1":
            standard_cmos_setup()
        elif choice == "6":
            print("Saving BIOS settings...")
            time.sleep(1)
            print("Exiting BIOS...")
            break
        elif choice == "7":
            toggle_fastboot()
        else:
            print("Feature not implemented in this BIOS version")
            time.sleep(1)

# === Boot Flow ===
print(f"{bios_name} v{bios_version}")
print("Performing system checks...")
time.sleep(BIOS_DELAY * 5)  # Slightly longer for initial checks

print(f"Testing {getattr(mb_module, 'mbMemSTR', 'Unknown')} system RAM...")
time.sleep(BIOS_DELAY * 10)

print("\nDetected Hardware:")
print(f"- CPU: {cpu_module.cName}")
print(f"- MB: {getattr(mb_module, 'mbName', 'Unknown')}")
print(f"- Storage: {get_primary_storage()}")
time.sleep(BIOS_DELAY * 5)
check_bios_prompt()

try:
    bios_ini = os.path.join(SYS_DIR, "bios.ini")
    if os.path.exists(bios_ini):
        print("\nFound BIOS configuration, booting system...")
        time.sleep(BIOS_DELAY * 5)
        sys.path.append(PROJECT_ROOT)
        import op3
        op3.main()
    else:
        print("\nNo BIOS configuration found")
        print("Press 1 to enter SETUP, any other key to continue...")
        if input() == "1":
            bios_menu()
        else:
            sys.path.append(PROJECT_ROOT)
            import op3
            op3.main()
except ImportError:
    print("\nError: Operating system not found!")
    input("Press Enter to enter BIOS setup...")
    bios_menu()