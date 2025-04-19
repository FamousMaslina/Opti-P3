mbName = "Modular 386 Motherboard"
mbMemINT = 2048
mbMemSTR = "2048KB"
mbSocketSupported = "386"
idcode = "KSADFAS"
bcode = "386basic"
import os
import re

portIDE1 = {  # Used for simulating HDDS/CDs
    "use": True,
    "hdd1name": "IDE Device",
    "hdd1storageINT": 64000,
    "hdd1storageSTR": "64000 KB",
    "idcode": "ASDAD21"
}

portIDE2 = {
    "use": True,
    "hdd2name": "IDE Device2",
    "hdd2storageINT": 64000,
    "hdd2storageSTR": "64000 KB",
    "idcode": "ASDAD21"
}

portFDC1 = {  # Used for simulating Floppies
    "use": True,
    "flo1name": "3.5 Floppy Drive",
    "firin": True  # Synonym to idcode
}

portFDC2 = {
    "use": True,
    "flo2name": "3.5 Floppy Drive",
    "firin": True
}

portPS2_1 = {  # Used for simulating keyboard/mouse
    "use": True,
    "keyName": "BASIC PS/2 KEYBOARD",
    "kkeyb": True
}

portPS2_2 = {
    "use": False
}

mbOnBoardCPU = False
mbOnBoardGPU = False

from importlib import import_module
def find_python_files(directory):
    files = os.listdir(directory)
    python_files = []
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.join(directory, file))
    return python_files

def find_variablesCPU(file_path):
    variables = []
    with open(file_path, "r") as f:
        for line in f:
            match = re.search(r"(asdawd2k3a403)", line)
            if match:
                variables.append(match.group(1))
    return variables

current = os.path.basename(__file__)
global cpu

def findCPU():
    global cpu
    cpu_directory = os.path.join(os.getcwd(), "cpus")  # Adjust if CPUs are in a subfolder
    if not os.path.exists(cpu_directory):  # Fallback to current directory if subfolder doesn't exist
        cpu_directory = os.getcwd()
    python_files = find_python_files(cpu_directory)  # Search for Python files in the CPU directory
    for file in python_files:
        if os.path.basename(file) not in ["identifier.py", "idmb.py", "op2.py", "bios.py", "hardwiz.py", os.path.basename(__file__)]:
            variables = find_variablesCPU(file)
            if variables:
                cpu = os.path.basename(file).replace(".py", "")
                with open("idcpu.py", "w") as f:
                    f.write("cpu = '{}'".format(cpu))
                return cpu
    return None
import sys
def find_bios(mb_bios_code):
    """Locate the BIOS file that matches the motherboard's required BIOS code"""
    bios_dir = os.path.join(os.getcwd(), "sys")  # BIOS files are in sys directory
    if not os.path.exists(bios_dir):
        return None
        
    for file in os.listdir(bios_dir):
        if file.endswith(".py") and file != "__init__.py":
            file_path = os.path.join(bios_dir, file)
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    # Search for bios_code = "phnx386" or similar
                    match = re.search(r'bios_code\s*=\s*["\']({})["\']'.format(mb_bios_code), content)
                    if match:
                        return file_path
            except:
                continue
    return None
def bios():
    global cpu
    print(f"BIOS is running in directory: {os.getcwd()}")
    
    # First check if motherboard requires specific BIOS
    try:
        mb_module = import_module("hw." + mb.replace('.py', ''))
        if hasattr(mb_module, 'reqBIOS'):
            bios_file = find_bios(mb_module.reqBIOS)
            if bios_file:
                # Load the required BIOS
                bios_name = os.path.basename(bios_file).replace('.py', '')
                bios_module = import_module(f"sys.{bios_name}")
                print(f"Loaded required BIOS: {bios_module.bios_name} {bios_module.bios_version}")
                return bios_module.bios()  # Run the BIOS initialization
            else:
                print(f"Warning: Required BIOS {mb_module.reqBIOS} not found")
    except Exception as e:
        print(f"BIOS compatibility check error: {e}")
    
    # Fall back to default CPU initialization
    cpu_file = findCPU()
    if cpu_file:
        try:
            # Add the directory containing the CPU module to PYTHONPATH
            cpu_directory = os.path.join(os.getcwd(), "cpus")  # Update this path as necessary
            if not os.path.exists(cpu_directory):  # Fallback to current directory
                cpu_directory = os.getcwd()
            sys.path.append(cpu_directory)

            cpu_module = import_module(cpu)
            print(f"Loaded CPU: {cpu_module.cName}")
        except ModuleNotFoundError as e:
            print(f"Error loading CPU module: {e}")
    else:
        print("No CPU found.")
