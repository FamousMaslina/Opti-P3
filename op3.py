#op3.py
import os
import re
import sys
import time
import configparser
import importlib.util
import random
from importlib import import_module
from os import name, system
import configparser
import os
from datetime import datetime
_opfs_spec = importlib.util.spec_from_file_location(
    'op3_opfs', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sys', 'opfs.py'))
_opfs_module = importlib.util.module_from_spec(_opfs_spec)
_opfs_spec.loader.exec_module(_opfs_module)
OPFS = _opfs_module.OPFS
osName = "Opti P3"
initial_directory = os.path.dirname(os.path.abspath(__file__))
current_directory = 'O:/'
import subprocess
op3vIST = "0.2.0"
op3vIINT = 0.2
CURRENT_DRIVE = 'O'
DRIVE_ROOTS = {'O': 'O:/'}
FLOPPY_LETTERS = set()
filesystem = OPFS(os.path.join(os.getcwd(), '.opfs'), working_directory=os.getcwd())

def setup_drives(mb_module=None):
    filesystem.load()
    if mb_module:
        ports = sorted(dir(mb_module), key=lambda attr: [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', attr)])
        for attr in ports:
            if not attr.startswith(('portIDE', 'portFDC')):
                continue
            port = getattr(mb_module, attr)
            if not isinstance(port, dict) or not port.get('use', False):
                continue
            kind = 'floppy' if attr.startswith('portFDC') else 'hdd'
            label = next((str(v) for k, v in port.items() if k.lower().endswith('name')), attr)
            filesystem.mount_device(attr, kind, label, port.get('drive_letter'))
    _sync_opfs()

def _sync_opfs():
    global CURRENT_DRIVE, current_directory, FLOPPY_LETTERS
    CURRENT_DRIVE = filesystem.current[0]
    current_directory = filesystem.current
    DRIVE_ROOTS.clear()
    DRIVE_ROOTS.update({letter: letter + ':/' for letter in filesystem.drives})
    FLOPPY_LETTERS = {letter for letter, info in filesystem.drives.items() if info['kind'] == 'floppy'}

def opfs_command(*args):
    if not args or args == ('drives',):
        for letter, drive in sorted(filesystem.drives.items()):
            print(f"{letter}:/  OPFS  {drive['kind']:<7} {drive['label']}")
    elif len(args) >= 3 and args[0] == 'add':
        filesystem.add_drive(args[1], args[2], ' '.join(args[3:]))
        _sync_opfs()
        print(f"Created OPFS drive {args[1].upper().rstrip(':')}:/")
    else:
        print('Usage: opfs [drives | add <letter> <hdd|floppy> [label]]')

def switch_drive(letter: str):
    cd(letter.upper().rstrip(':') + ':/')

def linebr(number):
   print("=" * number)
def linebr2(number):
   print("-" * number)
def cls():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

class HardwareManager:
    def __init__(self):
        self.hardware = {
            'cpu': None,
            'mb': None,
            'hd': None,
            'mon': None,
            'key': None,
            'flo': None,
            'gpu': None,
            'modem': None, 
            'sound': None,
            'battery': None,
            'laptop': None
        }
        self.loaded_modules = {}
        base_dir = os.path.dirname(__file__)
        self.hw_dir = os.path.join(os.path.dirname(__file__), "hw")
        self.hw_dir = os.path.join(base_dir, "hw")
        self.config_file = os.path.join(base_dir, "sys", "ini", "op3.ini")
        self.autostart_file = os.path.join(base_dir, "sys", "autostart.txt")
        sys.path.append(self.hw_dir)
        self.initialize_hardware()
        self.delay_app = 1.0 
        self.delay_in_app = 0.5
        self.init_cpu_timing()
        self.config = configparser.ConfigParser()
        self.config_file = os.path.join('sys', 'ini', 'op3.ini')
        self.initialize_config()
        self.autostart_file = os.path.join('sys', 'autostart.txt')
        self.initialize_autostart()

    def initialize_config(self):
        if not os.path.exists(self.config_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            self.config['user'] = {
                'computer_name': 'DEFAULT',
                'last_boot': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'debug_mode': '0'
            }
            self.config['sys'] = {
                'remids': '1',
                'autos': '1',
                'extensions': '1',
                'fancystart': '0',
                'fastboot': '0',
                'delay_app': '1.0', 
                'delay_in_app': '0.5'
            }
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read(self.config_file)
            if 'fastboot' not in self.config['sys']:
                self.config.set('sys', 'fastboot', '0')
            if 'delay_app' not in self.config['sys']:
                self.config.set('sys', 'delay_app', '1.0')
            if 'delay_in_app' not in self.config['sys']:
                self.config.set('sys', 'delay_in_app', '0.5')
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        if self.config.getboolean('sys', 'fastboot', fallback=False):
            self.delay_app = 0.1 
            self.delay_in_app = 0.05


    def rescan_specific_hardware(self):
        if not self.config.get('user', 'debug_mode', fallback='0') == '1':
            print("Error: Debug mode must be enabled to use this command")
            return
    
        print("\nRescanning specific hardware...")
    
        # Clear existing IDs
        for hw_type in ['gpu', 'sound', 'modem']:
            self.hardware[hw_type] = None
            id_file = os.path.join(self.hw_dir, f"id{hw_type}.py")
            if os.path.exists(id_file):
                os.remove(id_file)
    
        # Rescan
        hw_files = [f for f in os.listdir(self.hw_dir) if f.endswith('.py') and not f.startswith('id')]
    
        for file in hw_files:
            try:
                with open(os.path.join(self.hw_dir, file), 'r') as f:
                    content = f.read()
                
                    # GPU detection
                    if not self.hardware['gpu']:
                        if ('gName' in content and 'gVram' in content):
                            self.create_id_file('gpu', file)
                            print(f" - Detected GPU: {file}")
                            continue
                        
                    # Modem detection
                    if not self.hardware['modem']:
                        if ('modemname' in content or 'dialupadp' in content):
                            self.create_id_file('modem', file)
                            print(f" - Detected Modem: {file}")
                            continue
                        
                    # Sound card detection
                    if not self.hardware['sound']:
                        if ('soundName' in content or 'soundChip' in content):
                            self.create_id_file('sound', file)
                            print(f" - Detected Sound Card: {file}")
                        
            except Exception as e:
                print(f" - Error scanning {file}: {str(e)}")
    
        # Reload the modules
        self.import_hardware_modules()
        print("\nRescan complete!")


    def config_editor(self):
        clear()
        print("OP3 Configuration Editor")
        linebr(40)
        
        while True:
            for section in self.config.sections():
                print(f"[{section}]")
                for key, value in self.config.items(section):
                    print(f"  {key} = {value}")
                print()
            
            linebr(40)
            print("1. Edit value")
            print("2. Add new section")
            print("3. Add new key")
            print("4. Save and exit")
            print("5. Exit without saving")
            linebr(40)
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                section = input("Enter section name: ").strip()
                if section in self.config:
                    key = input("Enter key name: ").strip()
                    if key in self.config[section]:
                        new_value = input(f"Enter new value for {key}: ").strip()
                        self.config.set(section, key, new_value)
                        print("Value updated!")
                    else:
                        print("Key not found!")
                else:
                    print("Section not found!")
                time.sleep(1)
                clear()
                
            elif choice == "2":
                section = input("Enter new section name: ").strip()
                if section not in self.config:
                    self.config.add_section(section)
                    print("Section added!")
                else:
                    print("Section already exists!")
                time.sleep(1)
                clear()
                
            elif choice == "3":
                section = input("Enter section name: ").strip()
                if section in self.config:
                    key = input("Enter new key name: ").strip()
                    if key not in self.config[section]:
                        value = input(f"Enter value for {key}: ").strip()
                        self.config.set(section, key, value)
                        print("Key added!")
                    else:
                        print("Key already exists!")
                else:
                    print("Section not found!")
                time.sleep(1)
                clear()
                
            elif choice == "4":
                with open(self.config_file, 'w') as configfile:
                    self.config.write(configfile)
                print("Configuration saved!")
                time.sleep(1)
                break
                
            elif choice == "5":
                print("Changes discarded!")
                time.sleep(1)
                break
                
            else:
                print("Invalid option!")
                time.sleep(1)
                clear()

    def initialize_autostart(self):
        os.makedirs(os.path.dirname(self.autostart_file), exist_ok=True)
        if not os.path.exists(self.autostart_file):
            with open(self.autostart_file, 'w') as f:
                f.write("# OP3 Autostart commands\n")
                f.write("# One command per line\n")
                f.write("# Lines starting with # are comments\n\n")

    def run_autostart(self):
        if not self.config.getboolean('sys', 'autos', fallback=True):
            return
        
        if not os.path.exists(self.autostart_file):
            return
        
        print("\nRunning autostart commands...")
        linebr(40)
    
        try:
            with open(self.autostart_file, "r") as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    print(f"Executing: {line}")
                    try:
                        # Add small delay between commands
                        time.sleep(self.delay_in_app)
                    
                        # Execute the command
                        if line in self.get_valid_commands():
                            os.system(line)
                        else:
                            print(f"  ! Unknown command on line {line_num}")
                    except Exception as e:
                        print(f"  ! Error executing line {line_num}: {str(e)}")
                    
            linebr(40)
        except Exception as e:
            print(f"Autostart error: {str(e)}")

    def nameO(self):
        computer_name = self.config.get('user', 'computer_name', fallback='DEFAULT')
        print(f"{osName} {op3vIST} - {computer_name}")

    def set_computer_name(self, new_name):
        if 'user' not in self.config:
            self.config.add_section('user')
        self.config.set('user', 'computer_name', new_name)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        print(f"Computer name set to: {new_name}")

    def computername(self):
        print()
        new = input("Type in your desired name (or 'exit' to exit): ")
        if new.lower() != "exit":
            self.set_computer_name(new)
            print("Name set successfully!")
            
    def autostart(self):
        print("\n=== Autostart Manager ===")
        print("Current autostart commands:")
        try:
            with open(self.autostart_file, "r") as f:
                print(f.read())
        except FileNotFoundError:
            print("No autostart file found")
            
        print("\nOptions:")
        print("1. Add command")
        print("2. Clear all commands")
        print("3. Exit")
        
        choice = input("Select option: ").strip()
        if choice == "1":
            cmd = input("Enter command to add: ").strip()
            if cmd:
                with open(self.autostart_file, "a") as f:
                    f.write(f"{cmd}\n")
                print("Command added to autostart")
        elif choice == "2":
            with open(self.autostart_file, "w") as f:
                f.write("# OP3 Autostart commands\n")
            print("Autostart commands cleared")

    def load_extensions(self):
        extensions = {}
        extensions_folder = 'plugins'
        if os.path.exists(extensions_folder):
            for filename in os.listdir(extensions_folder):
                if filename.endswith('.py'):
                    module_name = filename[:-3]
                    try:
                        module = importlib.import_module(f'plugins.{module_name}')
                        if hasattr(module, 'commands'):
                            extensions.update(module.commands)
                    except Exception as e:
                        print(f"Failed to load extension {filename}: {str(e)}")
        return extensions

    def manage_extensions(self):
        extensions_folder = 'plugins'
        extensions_info = []

        if not os.path.exists(extensions_folder):
            print("\nNo plugins directory found")
            return

        for filename in os.listdir(extensions_folder):
            if filename.endswith('.py'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'plugins.{module_name}')
                    if hasattr(module, 'info') and hasattr(module, 'commands'):
                        module_info = module.info
                        module_info['commands'] = ', '.join(module.commands.keys())
                        extensions_info.append(module_info)
                except Exception as e:
                    print(f"Error loading plugin {filename}: {str(e)}")
        
        print("\n=== Installed Plugins ===")
        for ext in extensions_info:
            print(f"----------------------------------------")
            print(f"Title      : {ext['title']}")
            print(f"Version    : {ext['version']}")
            print(f"Author     : {ext['author']}")
            print(f"Description: {ext.get('description', 'No description available')}")
            print(f"Commands   : {ext['commands']}")
            print(f"----------------------------------------")

        while True:
            action = input("\nEnter 'delete <plugin>' or 'exit': ").strip().lower()
            if action == 'exit':
                break
            action_parts = action.split()
            if len(action_parts) != 2:
                print("Invalid command.")
                continue

            command, ext_name = action_parts

            if command == 'delete':
                ext_file = os.path.join(extensions_folder, ext_name + '.py')
                if os.path.exists(ext_file):
                    os.remove(ext_file)
                    print(f"Plugin '{ext_name}' deleted.")
                else:
                    print(f"Plugin '{ext_name}' not found.")
            else:
                print("Invalid command.")

    def init_cpu_timing(self):
        if 'cpu' in self.loaded_modules:
            cpu = self.loaded_modules['cpu']
            try:
                self.delay_app = 45 / cpu.cFreq
                self.delay_in_app = 15 / cpu.cFreq
            except AttributeError:
                print("Warning: CPU frequency not properly configured")
    def delay_before_print(self, delay_type='app'):
        delay = self.delay_in_app if delay_type == 'in_app' else self.delay_app
        time.sleep(delay)

    def scan_for_hardware(self):
        print("\nScanning hardware directory...")
        hw_files = [f for f in os.listdir(self.hw_dir) if f.endswith('.py') and not f.startswith('id')]
        
        for file in hw_files:
            try:
                with open(os.path.join(self.hw_dir, file), 'r') as f:
                    content = f.read()
                    
                    # Skip BIOS file explicitly
                    if file.lower() == 'bios.py':
                        continue
                        
                    # Laptop detection (should be checked first)
                    if not self.hardware['laptop']:
                        if ('isLaptop' in content or 'laptopModel' in content or 
                            'batteryCapacity' in content):
                            self.create_id_file('laptop', file)
                            print(f" - Detected Laptop: {file}")
                            #continue
                            
                    # Battery detection
                    if not self.hardware['battery']:
                        if ('batteryCapacity' in content or 'batteryType' in content):
                            self.create_id_file('battery', file)
                            print(f" - Detected Battery: {file}")
                            #continue
                        
                    # CPU detection
                    if not self.hardware['cpu']:
                        if ('cName' in content and 'cFreq' in content and 
                            ('asdawd2k3a403' in content or 'cFreqUnit' in content)):
                            self.create_id_file('cpu', file)
                            print(f" - Valid CPU detected: {file}")
                            #continue
                            
                    # Motherboard detection
                    if not self.hardware['mb']:
                        if ('mbName' in content and 
                            ('portIDE' in content or 'portFDC' in content or 'mbMemSTR' in content)):
                            self.create_id_file('mb', file)
                            print(f" - Detected Motherboard: {file}")
                            continue
                            
                    # Keyboard detection
                    if not self.hardware['key']:
                        if 'keyName' in content or 'kkeyb' in content:
                            self.create_id_file('key', file)
                            print(f" - Detected Keyboard: {file}")
                            continue
                            
                    # Monitor detection
                    if not self.hardware['mon']:
                        if 'monitorName' in content or 'monitorID' in content:
                            self.create_id_file('mon', file)
                            print(f" - Detected Monitor: {file}")
                            continue
                            
                    # Hard drive detection
                    if not self.hardware['hd']:
                        if 'hddname' in content or 'hddspace' in content:
                            self.create_id_file('hd', file)
                            print(f" - Detected Storage: {file}")
                            continue
                            
                    # Floppy detection
                    if not self.hardware['flo']:
                        if 'flo1name' in content or 'firin' in content:
                            self.create_id_file('flo', file)
                            print(f" - Detected Floppy: {file}")
                    # GPU detection
                    if not self.hardware['gpu']:
                        if ('gName' in content and 'gVram' in content):
                            self.create_id_file('gpu', file)
                            print(f" - Detected GPU: {file}")
                            #continue
                        
                    # Modem detection
                    if not self.hardware['modem']:
                        if ('modemname' in content or 'dialupadp' in content):
                            self.create_id_file('modem', file)
                            print(f" - Detected Modem: {file}")
                            continue
                    
                    # Sound card detection
                    if not self.hardware['sound']:
                        if ('soundName' in content or 'soundChip' in content):
                            self.create_id_file('sound', file)
                            print(f" - Detected Sound Card: {file}")
                            
            except Exception as e:
                print(f" - Error scanning {file}: {str(e)}")

    def create_id_file(self, hw_type, filename):
        with open(os.path.join(self.hw_dir, f"id{hw_type}.py"), 'w') as f:
            f.write(f"{hw_type} = '{filename}'")
        self.hardware[hw_type] = filename

    def initialize_hardware(self):
        print("\nInitializing hardware...")
        
        self.scan_for_hardware()
        
        self.load_id_files()
        self.import_hardware_modules()
        self.check_essential_components()

    def load_id_files(self):
        print("\nLoading hardware IDs...")
        for hw_type in self.hardware.keys():
            id_file = os.path.join(self.hw_dir, f"id{hw_type}.py")
            if os.path.exists(id_file):
                try:
                    with open(id_file, 'r') as f:
                        content = f.read()
                        match = re.search(r"{}\s*=\s*'([^']+)'".format(hw_type), content)
                        if match:
                            self.hardware[hw_type] = match.group(1)
                            print(f" - Loaded {hw_type.upper()} ID: {match.group(1)}")
                except Exception as e:
                    print(f" - Error reading {hw_type} ID file: {str(e)}")

    def import_hardware_modules(self):
        print("\nImporting hardware modules...")
        for hw_type, hw_file in self.hardware.items():
            if hw_file and hw_file.lower() != 'bios.py':  # Skip BIOS file
                try:
                    module_name = hw_file.replace('.py', '')
                    module = import_module(f"hw.{module_name}")
                    
                    if hw_type == 'cpu':
                        if not hasattr(module, 'cName') or not hasattr(module, 'cFreq'):
                            raise AttributeError("Invalid CPU module - missing required attributes")
                    elif hw_type == 'mb':
                        if not hasattr(module, 'mbName'):
                            raise AttributeError("Invalid motherboard module - missing mbName")
                    
                    self.loaded_modules[hw_type] = module
                    print(f" - Successfully imported {hw_type.upper()}: {module_name}")
                except Exception as e:
                    print(f" - Failed to import {hw_type} module: {str(e)}")
                    self.hardware[hw_type] = None
                    id_file = os.path.join(self.hw_dir, f"id{hw_type}.py")
                    if os.path.exists(id_file):
                        os.remove(id_file)

    def check_essential_components(self):
        print("\nVerifying essential components...")
        if 'cpu' not in self.loaded_modules:
            print(" !!! ERROR: No valid CPU detected - system cannot boot !!!")
        if 'mb' not in self.loaded_modules:
            print(" !!! WARNING: No valid motherboard detected - limited functionality !!!")

    def get_component(self, name):
        return self.loaded_modules.get(name)

hw_manager = None


def _extract_ide_drives(mb_module):
    drives = []
    if not mb_module:
        return drives
    for attr in dir(mb_module):
        if attr.startswith('portIDE'):
            port = getattr(mb_module, attr)
            if isinstance(port, dict) and port.get('use', False):
                # name: first key that ends with 'name'
                name = next((v for k, v in port.items() if k.lower().endswith('name')), 'IDE Device')
                # human size string if available, else INT → "NNN KB"
                size_str = next((v for k, v in port.items() if k.lower().endswith('storagestr')), None)
                if not size_str:
                    size_int = next((v for k, v in port.items() if 'storage' in k.lower() and isinstance(v, int)), None)
                    size_str = f"{size_int} KB" if isinstance(size_int, int) else "Unknown"
                drives.append((name, size_str))
    return drives


def batteryinfo():
    battery = hw_manager.get_component('battery')
    laptop = hw_manager.get_component('laptop')
    
    if laptop:
        print("\nLaptop Information:")
        print(f"Model: {getattr(laptop, 'laptopModel', 'Unknown')}")
        print(f"Manufacturer: {getattr(laptop, 'laptopOEM', 'Unknown')}")
        print(f"Screen Size: {getattr(laptop, 'screenSize', '?')}\"")
    
    if battery:
        print("\nBattery Information:")
        print(f"Type: {getattr(battery, 'batteryType', 'Unknown')}")
        print(f"Capacity: {getattr(battery, 'batteryCapacity', '?')} mAh")
        print(f"Current Charge: {getattr(battery, 'currentCharge', '100')}%")
        print(f"Status: {getattr(battery, 'batteryStatus', 'Charging' if random.random() > 0.5 else 'Discharging')}")
    else:
        print("\nNo battery detected - desktop system")
    print()

def powerstatus():
    battery = hw_manager.get_component('battery')
    if battery:
        charge = int(getattr(battery, 'currentCharge', '100'))
        status = getattr(battery, 'batteryStatus', 'Charging' if random.random() > 0.5 else 'Discharging')
        
        print("\nPower Status:")
        print(f"Battery: {charge}% {'🔌' if status == 'Charging' else '🔋'}")
        
        # Simple battery visualization
        filled = int(charge / 10)
        print(f"[{'█' * filled}{' ' * (10 - filled)}]")
        
        if status == 'Charging':
            print("Status: Charging (AC power connected)")
        else:
            remaining = random.randint(1, 6)  # Simulate remaining time
            print(f"Estimated remaining: {remaining}h {random.randint(0, 59)}m")
    else:
        print("\nAC power connected (desktop system)")
    print()


def create_floppy_drives(mb_module):
    """Compatibility entry point: mount all configured OPFS storage devices."""
    setup_drives(mb_module)


def init_hw():
    global hw_manager

    if hw_manager is not None:
        return

    hw_manager = HardwareManager()

    cpu = hw_manager.get_component('cpu')
    mb = hw_manager.get_component('mb')
    hd = hw_manager.get_component('hd')
    gpu = hw_manager.get_component('gpu')
    modem = hw_manager.get_component('modem')
    sound = hw_manager.get_component('sound')
    
    print("\n=== Hardware Summary ===")
    if cpu:
        print(f"CPU: {cpu.cName} @ {getattr(cpu, 'cFreqS', '?')}{getattr(cpu, 'cFreqUnit', 'MHz')}")
    else:
        print("CPU: Not detected")
    
    if mb:
        print(f"Motherboard: {mb.mbName}")
        print(f"Memory: {getattr(mb, 'mbMemSTR', 'Unknown')}")
    else:
        print("Motherboard: Not detected")
    
    drives = _extract_ide_drives(mb)
    if drives:
        print("Storage:")
        for i, (name, size) in enumerate(drives, 1):
            print(f"  {i}. {name} ({size})")
    else:
        print("Storage: No hard drive detected")
        
    if gpu:
        print(f"GPU: {getattr(gpu, 'gName', 'Unknown')} ({getattr(gpu, 'gVram', '?')}MB VRAM)")
    else:
        print("GPU: Not detected")
        
    if modem:
        print(f"Modem: {getattr(modem, 'modemname', 'Unknown')} ({getattr(modem, 'modemspeeds', '?')})")
    else:
        print("Modem: Not detected")
        
    if sound:
        print(f"Sound Card: {getattr(sound, 'soundName', 'Unknown')}")
    else:
        print("Sound Card: Not detected")
def sleep_time_app_load():
    if hw_manager and hw_manager.sleep_time_app_load:
        return hw_manager.sleep_time_app_load
    return 1.0  # Default value

def sleep_time_in_app_load():
    if hw_manager and hw_manager.sleep_time_in_app_load:
        return hw_manager.sleep_time_in_app_load
    return 0.5  # Default value



def helloworld():
    hw_manager.delay_before_print('in_app')
    print("It works!!!")


def nameO():
    print("Opti P3", op3vIST)


def create_template(template_name):
    template_content = f"""\

import sys
import os

from op3 import cls, clear, info, init_hw

def template_function():
    print("Template function called")
    cls()
    init_hw()
    info()
    print("This is how you interact with op3.py")

if __name__ == "__main__":
    template_function()
"""

    template_path = filesystem.resolve(f"{template_name}.py")
    filesystem.host_path(template_path).write_text(template_content, encoding='utf-8')
    print(f"Template file '{template_path}' created successfully.")

def rmdir(folder_name):
    _file_operation('remove directory', folder_name, lambda: filesystem.remove(folder_name, directory=True))


def delete_file(file_name):
    _file_operation('delete file', file_name, lambda: filesystem.remove(file_name))


def gpuinfo():
    gpu = hw_manager.get_component('gpu')
    if gpu:
        print("\nGPU Information:")
        print(f"Name: {getattr(gpu, 'gName', 'Unknown')}")
        print(f"VRAM: {getattr(gpu, 'gVram', '?')}MB")
        print(f"Speed: {getattr(gpu, 'gSpeed', '?')}MHz")
        print(f"Pixel Shaders: {getattr(gpu, 'gps', '?')}")
        print(f"Vertex Shaders: {getattr(gpu, 'gvs', '?')}")
        print(f"ROPs: {getattr(gpu, 'grop', '?')}")
    else:
        print("\nNo GPU detected")
    print()

def modeminfo():
    modem = hw_manager.get_component('modem')
    if modem:
        print("\nModem Information:")
        print(f"Name: {getattr(modem, 'modemname', 'Unknown')}")
        print(f"Type: {getattr(modem, 'dialupadp', 'Unknown')}")
        print(f"Speed: {getattr(modem, 'modemspeeds', 'Unknown')}")
    else:
        print("\nNo modem detected")
    print()
def soundinfo():
    sound = hw_manager.get_component('sound')
    if sound:
        print("\nSound Card Information:")
        print(f"Name: {getattr(sound, 'soundName', 'Unknown')}")
        print(f"Chip: {getattr(sound, 'soundChip', 'Unknown')}")
        print(f"Format: {getattr(sound, 'soundDF', 'Unknown')}")
        print(f"Stereo: {'Yes' if getattr(sound, 'stereo', False) else 'No'}")
    else:
        print("\nNo sound card detected")
    print()
def connect_internet():
    modem = hw_manager.get_component('modem')
    if modem:
        print(f"\nConnecting via {getattr(modem, 'modemname', 'modem')}...")
        print("Dialing... CONNECTED!")
    else:
        print("\nNo modem detected - cannot connect to internet")
    print()


def toggle_debug_mode():
    """Toggle debug mode on/off"""
    current = hw_manager.config.get('user', 'debug_mode', fallback='0')
    new_value = '1' if current == '0' else '0'
    hw_manager.config.set('user', 'debug_mode', new_value)
    with open(hw_manager.config_file, 'w') as configfile:
        hw_manager.config.write(configfile)
    print(f"Debug mode {'enabled' if new_value == '1' else 'disabled'}")
    if new_value == '1':
        print("Warning: Debug mode may expose sensitive information!")

def is_debug_mode():
    """Check if debug mode is enabled"""
    return hw_manager.config.get('user', 'debug_mode', fallback='0') == '1'

def show_variables():
    """Display all available variables when in debug mode"""
    if not is_debug_mode():
        print("Debug mode is disabled. Use 'debug' command to enable.")
        return
    
    print("\n=== System Variables ===")
    linebr(40)
    
    print("\n[Core Variables]")
    print(f"osName: {osName}")
    print(f"op3vIST: {op3vIST}")
    print(f"op3vIINT: {op3vIINT}")
    print(f"initial_directory: {initial_directory}")
    print(f"current_directory: {current_directory}")

    print("\n[Hardware Manager]")
    print(f"hw_manager.delay_app: {hw_manager.delay_app}")
    print(f"hw_manager.delay_in_app: {hw_manager.delay_in_app}")
    print("hw_manager.hardware:", {k:v for k,v in hw_manager.hardware.items()})

    print("\n[Config Values]")
    for section in hw_manager.config.sections():
        print(f"[{section}]")
        for key, value in hw_manager.config.items(section):
            print(f"  {key}: {value}")
    
    linebr(40)
    print("\nUse 'set [variable] [value]' to modify variables")
    print("Example: 'set osName NewName'")

def set_variable(variable, value):
    if not is_debug_mode():
        print("Debug mode is disabled. Use 'debug' command to enable.")
        return
    
    variable = variable.lower()
    success = False
    
    # Handle core variables
    if variable == "osname":
        global osName
        osName = value
        success = True
    elif variable == "op3vist":
        global op3vIST
        op3vIST = value
        success = True
    elif variable == "initial_directory":
        global initial_directory
        initial_directory = value
        success = True
    elif variable == "current_directory":
        global current_directory
        current_directory = value
        success = True
        
    # Handle hardware manager delays
    elif variable == "hw_manager.delay_app":
        try:
            hw_manager.delay_app = float(value)
            success = True
        except ValueError:
            print("Error: delay_app must be a number")
    elif variable == "hw_manager.delay_in_app":
        try:
            hw_manager.delay_in_app = float(value)
            success = True
        except ValueError:
            print("Error: delay_in_app must be a number")
            
    # Handle config values (section.key format)
    elif '.' in variable:
        section, key = variable.split('.', 1)
        if section in hw_manager.config and key in hw_manager.config[section]:
            hw_manager.config.set(section, key, value)
            with open(hw_manager.config_file, 'w') as configfile:
                hw_manager.config.write(configfile)
            success = True
    
    if success:
        print(f"Variable '{variable}' set to '{value}'")
    else:
        print(f"Variable '{variable}' not found or cannot be modified")


def main():
    global hw_manager
    if hw_manager is None:
        init_hw()
    if not filesystem.drives:
        setup_drives(hw_manager.get_component('mb'))
    cls()
    nameO()
    config = configparser.ConfigParser()
    config_file = os.path.join('sys', 'ini', 'op3.ini')
    if not os.path.exists(config_file):
        config['sys'] = {
            'extensions': '1',
            'fancystart': '0',
            'remids': '1',
            'fastboot': '0'
        }
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            config.write(f)
    else:
        config.read(config_file)
    extensions = {}
    if config.get('sys', 'extensions', fallback='1') == '1':
        extensions = hw_manager.load_extensions()
    command_mappings = {
        'helloworld': helloworld,
        'info': info,
        'bios': bios_menu_cmd,
        'computername': hw_manager.computername,
        'autostart': hw_manager.autostart,
        'name': hw_manager.nameO,
        'cls': cls,
        'clear': cls,
        'manage_extensions': manage_extensions,
        'exit': lambda: exit(0),
        'reboot': lambda: [print("Rebooting..."), time.sleep(1), main()],
        'shutdown': lambda: [print("Shutting down..."), time.sleep(1), exit(0)],
        'dvcman': lambda: subprocess.run([sys.executable, os.path.join('sys', 'dvcman.py')]),
        'opfs': opfs_command,
        'drives': opfs_command,
        'dir': ls,
        'ls': ls,
        'cd': cd,
        'mkdir': mkdir,
        'touch': touch,
        'edit': edit,
        'rmdir': rmdir,
        'deldir': rmdir,
        'root': root,
        'config': hw_manager.config_editor,
        'configure': hw_manager.config_editor,
        'settings': hw_manager.config_editor,
        'gpuinfo': gpuinfo,
        'modeminfo': modeminfo,
        'soundinfo': soundinfo,
        'internet': connect_internet,
        'debug': toggle_debug_mode,
        'var': show_variables,
        'set': set_variable,
        'battery':batteryinfo,
        'power':powerstatus,
        'laptopinfo':batteryinfo,
        'rescanhw': lambda: hw_manager.rescan_specific_hardware(),
        'help': lambda args=None: subprocess.run(
        [sys.executable, os.path.join('sys', 'help.py'), args[0]] if args else 
        [sys.executable, os.path.join('sys', 'help.py')]
        ),
        '?': lambda args=None: subprocess.run(
        [sys.executable, os.path.join('sys', 'help.py'), args[0]] if args else 
        [sys.executable, os.path.join('sys', 'help.py')]
    )
    }

    while True:
        debug_indicator = " [DEBUG]" if is_debug_mode() else ""
        prompt = f"{filesystem.current}{debug_indicator}> "

        try:
            inp = input(prompt).strip()
            if not inp:
                continue

            # Allow bare "A:" / "B:" to switch drives
            if len(inp) == 2 and inp[1] == ':' and inp[0].isalpha():
                switch_drive(inp[0])
                continue

            parts = inp.split()
            cmd_raw = parts[0]
            cmd = cmd_raw.lower()
            args = parts[1:] if len(parts) > 1 else []

            if cmd == 'set' and len(args) >= 2:
                set_variable(args[0], ' '.join(args[1:]))
                continue

            if cmd in ('del', 'delete', 'rm'):
                if args:
                    delete_file(' '.join(args).strip('"'))
                else:
                    print("Error: Missing filename (usage: del <filename>)")
                continue
            
            if cmd in command_mappings:
                if cmd == 'opfs':
                    opfs_command(*args)
                elif cmd == 'edit':
                    edit(' '.join(args).strip('"') or None)
                elif cmd in ('cd', 'mkdir', 'touch', 'rmdir', 'deldir'):
                    if args:
                        command_mappings[cmd](' '.join(args).strip('"'))
                    else:
                        print(f'Usage: {cmd} <path>')
                else:
                    command_mappings[cmd]()
            elif cmd in extensions:
                try:
                    extensions[cmd](*args)
                except Exception as e:
                    print(f"Error executing plugin command: {str(e)}")

            elif cmd == 'run' and args:
                file_name = ' '.join(args).strip('"')
                program_path = filesystem.host_path(file_name)
                if program_path.is_file():
                    program_env = os.environ.copy()
                    program_env['PYTHONPATH'] = os.pathsep.join(
                        filter(None, [initial_directory, program_env.get('PYTHONPATH')]))
                    subprocess.run([sys.executable, str(program_path)],
                                   cwd=str(filesystem.host_path()), env=program_env)
                else:
                    print(f"Program not found: {filesystem.resolve(file_name)}")

            elif cmd == 'create-template' and args:
                create_template(' '.join(args).strip('"'))

            else:
                print(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'shutdown' to quit")
        except (OSError, ValueError) as e:
            _opfs_error(e)
        except Exception as e:
            print(f"Error: {str(e)}")

def edit(filename=None):
    from programs.edit import edit_file
    edit_file(filesystem, filename)


def ls():
    try:
        print(f"\nDirectory of {filesystem.current} (OPFS)\n")
        print(f"{'Type':<8} {'Name':<20} {'Size':>10}")
        print('-' * 40)
        for item, directory, size in filesystem.listdir():
            shown_size = '' if directory else f'{size:,}'
            shown_type = '<DIR>' if directory else ''
            print(f'{shown_type:<8} {item:<20} {shown_size:>10}')
        print()
    except (OSError, ValueError) as error:
        _opfs_error(error)


def cd(folder_name):
    try:
        filesystem.chdir('/' if folder_name.lower() == 'root' else folder_name)
        _sync_opfs()
    except (OSError, ValueError) as error:
        _opfs_error(error)


def mkdir(folder_name):
    _file_operation('create directory', folder_name, lambda: filesystem.mkdir(folder_name))


def touch(file_name):
    _file_operation('create file', file_name, lambda: filesystem.touch(file_name))


def root():
    cd('/')
    print(f'Returned to {filesystem.current}')


def _opfs_error(error):
    # OSError text includes backing host paths; expose only its reason.
    reason = error.strerror if isinstance(error, OSError) else str(error)
    print(f'OPFS: {reason}')


def _file_operation(action, path, operation):
    try:
        operation()
        print(f'OPFS: {action}: {filesystem.resolve(path)}')
    except (OSError, ValueError) as error:
        _opfs_error(error)


def manage_extensions():
    hw_manager.manage_extensions()

def mainBoot():
    cpu = hw_manager.get_component('cpu')
    mb = hw_manager.get_component('mb')
    
    if not cpu:
        print("\nBOOT FAILED: Essential hardware missing (CPU)")
        return
    
    hw_manager.delay_before_print('app')
    print("\nSystem booting...")

    try:
        setup_drives(mb)

        hw_manager.delay_before_print('in_app')
        print(f" - CPU: {cpu.cName} @ {getattr(cpu, 'cFreqS', '?')}{getattr(cpu, 'cFreqUnit', 'MHz')}")
        
        if mb:
            hw_manager.delay_before_print('in_app')
            print(f" - Motherboard: {mb.mbName}")
        else:
            hw_manager.delay_before_print('in_app')
            print(" - WARNING: Running without motherboard detection")
        
        hw_manager.delay_before_print('app')
        print("\nSystem ready!")
        main()
    except AttributeError as e:
        hw_manager.delay_before_print('app')
        print(f"\nBOOT ERROR: {str(e)}")
        print("System halted")
import subprocess

def bios():
    print("Initializing BIOS...")

    bios_path = os.path.join("hw", "bios.py")
    
    if not os.path.exists(bios_path):
        print("BIOS not found in hw directory")
        return

    try:
        result = subprocess.run(
            [sys.executable, bios_path],
            check=True,
            cwd=os.getcwd()
        )
    except subprocess.CalledProcessError as e:
        print(f"BIOS execution failed with return code {e.returncode}")
    except Exception as e:
        print(f"Unexpected error running BIOS: {e}")

def bios_menu_cmd():
    print("Initializing BIOS (menu)...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    bios_path = os.path.join(base_dir, "hw", "bios.py")

    if not os.path.exists(bios_path):
        print("BIOS not found in hw directory")
        return

    try:
        subprocess.run(
            [sys.executable, bios_path, "--menu"],
            check=True,
            cwd=base_dir
        )
    except subprocess.CalledProcessError as e:
        print(f"BIOS setup exited with code {e.returncode}")
    except Exception as e:
        print(f"Unexpected error running BIOS: {e}")


def info():
        print()
        cpu = hw_manager.get_component('cpu')
        print("Opti P3", op3vIST)
        print("Running on", cpu.cName, "at", getattr(cpu, 'cFreqS', '?') + getattr(cpu, 'cFreqUnit', 'MHz'))
        print()
    
if __name__ == "__main__":
    if not os.path.exists("hw"):
        os.makedirs("hw")
        print("Created hw directory")    
    cls()
    bios()
    init_hw()
    mainBoot()
