import os
import re
from importlib import import_module

def find_python_files(directory):
    files = os.listdir(directory)
    python_files = [os.path.join(directory, file) for file in files if file.endswith(".py")]
    return python_files

def find_variables_mb(file_path):
    variables = []
    with open(file_path, "r") as f:
        for line in f:
            match = re.search(r"(KSADFAS)", line)
            if match:
                variables.append(match.group(1))
    return variables

def find_mb():
    """Finds motherboard files based on ID and returns their paths."""
    hw_folder = os.path.join(os.getcwd(), "hw")
    python_files = find_python_files(hw_folder)
    for file in python_files:
        variables = find_variables_mb(file)
        if variables:
            return file  # Return the first file found with matching variables
    return None

def identify_ports_and_devices(mb_file):
    """Identifies ports and connected devices from the motherboard file."""
    with open(mb_file, "r") as f:
        content = f.read()

    ports = {}

    # Identify IDE ports
    ide_matches = re.findall(r"portIDE\d+ = \{([^}]+)\}", content)
    for i, ide in enumerate(ide_matches, start=1):
        port_name = f"IDE{i}"
        ports[port_name] = {}
        for line in ide.split(','):
            key_value = line.split(":")
            if len(key_value) == 2:
                key, value = key_value
                ports[port_name][key.strip()] = value.strip()

    # Identify FDC ports
    fdc_matches = re.findall(r"portFDC\d+ = \{([^}]+)\}", content)
    for i, fdc in enumerate(fdc_matches, start=1):
        port_name = f"FDC{i}"
        ports[port_name] = {}
        for line in fdc.split(','):
            key_value = line.split(":")
            if len(key_value) == 2:
                key, value = key_value
                ports[port_name][key.strip()] = value.strip()

    # Identify PS/2 ports
    ps2_matches = re.findall(r"portPS2_\d+ = \{([^}]+)\}", content)
    for i, ps2 in enumerate(ps2_matches, start=1):
        port_name = f"PS2_{i}"
        ports[port_name] = {}
        for line in ps2.split(','):
            key_value = line.split(":")
            if len(key_value) == 2:
                key, value = key_value
                ports[port_name][key.strip()] = value.strip()

    # Filter and display ports based on 'use' status
    filtered_ports = {}
    for port, details in ports.items():
        use_status = details.get("\"use\"", "True").strip(' \"')
        if use_status == "False":
            filtered_ports[port] = {"name": details.get("\"hdd1name\"", details.get("\"flo1name\"", "Unknown"))}
        else:
            filtered_ports[port] = details

    return filtered_ports

def load_and_run_bios(mb_file):
    module_name = os.path.basename(mb_file).replace(".py", "")
    mb_module = import_module(f"hw.{module_name}")
    print(f"Running BIOS for {mb_file}")

    # Ensure the correct working directory for the BIOS function
    os.chdir(os.path.dirname(mb_file))
    mb_module.bios()

if __name__ == "__main__":
    motherboard = find_mb()
    if not motherboard:
        print("No motherboard found.")
    else:
        print("Motherboard found:", motherboard)

        # Identify ports and devices
        ports = identify_ports_and_devices(motherboard)
        print("Identified Ports and Devices:")
        for port, details in ports.items():
            print(f"{port}: {details}")

        # Load and run BIOS
        load_and_run_bios(motherboard)

