# sys/bios.py
import os
import time
import sys
from importlib import import_module

# Add hw directory to path
sys.path.append(os.path.join(os.getcwd(), "hw"))

# Clean up old identification files
def clean_ids():
    id_files = ["idcpu.py", "idmb.py", "idhd.py", "idmon.py", "idkey.py"]
    for file in id_files:
        try:
            os.remove(os.path.join("hw", file))
        except FileNotFoundError:
            pass

clean_ids()
time.sleep(0.2)

# BIOS Configuration
bios_name = "Phoenix 386 BIOS"
bios_version = "3.1.0"
bios_code = "phnx386"  # This must match mb_module.bcode in the MB file
required_mb_code = "386basic"  # Expected motherboard code

# Hardware detection functions
def detect_hardware():
    """Detect all hardware components and create ID files in hw directory."""
    hw_types = [
        ("asdawd2k3a403", "idcpu.py", "cpu"),
        ("KSADFAS", "idmb.py", "mb"),
        ("kajsaed", "idhd.py", "hd"),
        ("mmmnni", "idmon.py", "mon"),
        ("kkeyb", "idkey.py", "key")
    ]
    
    hw_dir = os.path.join(os.getcwd(), "hw")
    for identifier, id_file, var_name in hw_types:
        for file in os.listdir(hw_dir):
            if file.endswith(".py") and file not in ["bios.py", "op3.py"]:
                with open(os.path.join(hw_dir, file), "r") as f:
                    if identifier in f.read():
                        with open(os.path.join("hw", id_file), "w") as idf:
                            idf.write(f"{var_name} = '{file}'")

detect_hardware()
time.sleep(0.2)

# Import detected hardware
sys.path.append(os.path.join(os.getcwd(), "hw"))
from hw.idcpu import cpu
from hw.idmb import mb
from hw.idhd import hd
from hw.idmon import mon
from hw.idkey import key

# Load hardware modules
hw_dir = os.path.join(os.getcwd(), "hw")
sys.path.append(hw_dir)
mb_module = import_module(f"hw.{mb.replace('.py', '')}")
cpu_module = import_module(f"hw.{cpu.replace('.py', '')}")
hd_module = import_module(f"hw.{hd.replace('.py', '')}")
mon_module = import_module(f"hw.{mon.replace('.py', '')}")
key_module = import_module(f"hw.{key.replace('.py', '')}")

# BIOS-Motherboard compatibility check
if not hasattr(mb_module, 'bcode') or mb_module.bcode != required_mb_code:
    print(f"{bios_name} ERROR: Incompatible motherboard!")
    print(f"Expected MB code: {required_mb_code}")
    print(f"Found MB code: {getattr(mb_module, 'bcode', 'None')}")
    while True:  # Halt system
        time.sleep(1)

# System information display
def show_system_info():
    print(f"\n{bios_name} v{bios_version}")
    print("=========================")
    print(f"Motherboard: {getattr(mb_module, 'mbName', 'Unknown')}")
    print(f"CPU: {cpu_module.cName} @ {cpu_module.cFreqS}{cpu_module.cFreqUnit}")
    print(f"Memory: {getattr(mb_module, 'mbMemSTR', 'Unknown')}")
    print(f"Primary Storage: {getattr(hd_module, 'hddname', 'None')}")
    print(f"Monitor: {getattr(mon_module, 'monitorName', 'Standard VGA')}")
    print("=========================\n")

# BIOS Menu
def bios_menu():
    while True:
        show_system_info()
        print("Main BIOS Menu")
        print("1. Standard CMOS Setup")
        print("2. BIOS Features Setup")
        print("3. Chipset Features Setup")
        print("4. Power Management Setup")
        print("5. Load Setup Defaults")
        print("6. Save & Exit Setup")
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            standard_cmos_setup()
        elif choice == "6":
            print("Saving BIOS settings...")
            time.sleep(1)
            print("Exiting BIOS...")
            break
        else:
            print("Feature not implemented in this BIOS version")

def standard_cmos_setup():
    print("\nStandard CMOS Setup")
    print("------------------")
    print(f"Date: {time.strftime('%m/%d/%Y')}")
    print(f"Time: {time.strftime('%H:%M:%S')}")
    print("\nDrive Configuration:")
    
    # Detect IDE devices
    ide_devices = []
    for attr in dir(mb_module):
        if attr.startswith('portIDE'):
            port = getattr(mb_module, attr)
            if isinstance(port, dict) and port.get('use', False):
                device_name = port.get('hdd1name', 'IDE Device')
                device_size = port.get('hdd1storageSTR', 'Unknown')
                ide_devices.append(f"{attr}: {device_name} ({device_size})")
    
    print("\n".join(ide_devices) if ide_devices else "No IDE devices detected")
    
    input("\nPress Enter to return to main menu...")

# Boot sequence
print(f"{bios_name} v{bios_version}")
print("Performing system checks...")
time.sleep(1)

# Memory test
print(f"Testing {getattr(mb_module, 'mbMemSTR', 'Unknown')} system RAM...")
time.sleep(2)

# Hardware detection
print("\nDetected Hardware:")
print(f"- CPU: {cpu_module.cName}")
print(f"- MB: {getattr(mb_module, 'mbName', 'Unknown')}")
print(f"- Storage: {getattr(hd_module, 'hddname', 'None')}")

time.sleep(2)

# Enter BIOS menu or boot
try:
    if os.path.exists(os.path.join("sys", "bios.ini")):
        # Load configuration and boot
        print("\nFound BIOS configuration, booting system...")
        time.sleep(1)
        import op3
        op3.main()
    else:
        # Enter setup
        print("\nNo BIOS configuration found")
        print("Press DEL to enter SETUP, any other key to continue...")
        if input() == "DEL":
            bios_menu()
        else:
            import op3
            op3.main()
except ImportError:
    print("\nError: Operating system not found!")
    input("Press Enter to enter BIOS setup...")
    bios_menu()