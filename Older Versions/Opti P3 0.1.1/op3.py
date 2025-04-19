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
osName = "Opti P3"
initial_directory = os.getcwd()
current_directory = initial_directory
import subprocess
op3vIST = "0.1.1"
op3vIINT = 0.1
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
            'flo': None
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
                'last_boot': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        if not os.path.exists(self.autostart_file):
            os.makedirs(os.path.dirname(self.autostart_file), exist_ok=True)
            with open(self.autostart_file, 'w') as f:
                f.write("# OP3 Autostart commands\n")

    def run_autostart(self):
        if self.config.get('sys', 'autos', fallback='1') == '1':
            try:
                with open(self.autostart_file, "r") as file:
                    for line in file:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            try:
                                time.sleep(0.5)
                                os.system(line)
                            except Exception as e:
                                print(f"Autostart error executing '{line}': {str(e)}")
            except FileNotFoundError:
                pass

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
                        
                    # CPU detection
                    if not self.hardware['cpu']:
                        if ('cName' in content and 'cFreq' in content and 
                            ('asdawd2k3a403' in content or 'cFreqUnit' in content)):
                            self.create_id_file('cpu', file)
                            print(f" - Valid CPU detected: {file}")
                            continue
                            
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

def create_floppy_drives(mb_module):
    floppy_ports = []
    
    for attr in dir(mb_module):
        if attr.startswith('portFDC'):
            port = getattr(mb_module, attr)
            if isinstance(port, dict) and port.get('use', False):
                floppy_ports.append(port)
    
    drive_letters = ['A', 'B', 'C', 'D']
    for i, port in enumerate(floppy_ports[:4]):  # Max 4 drives (A-D)
        drive_name = drive_letters[i]
        try:
            os.makedirs(drive_name, exist_ok=True)
            print(f"Created floppy drive: {drive_name} ({port.get('flo1name', 'Unnamed')})")
        except OSError as e:
            print(f"Failed to create drive {drive_name}: {e}")


def init_hw():
    global hw_manager

    if hw_manager is not None:
        return

    hw_manager = HardwareManager()

    cpu = hw_manager.get_component('cpu')
    mb = hw_manager.get_component('mb')
    hd = hw_manager.get_component('hd')
    
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
    
    if hd:
        print(f"Storage: {getattr(hd, 'hddname', 'Unknown')} ({getattr(hd, 'hddspace', '?')}KB)")
    else:
        print("Storage: No hard drive detected")
def sleep_time_app_load():
    if hw_manager and hw_manager.sleep_time_app_load:
        return hw_manager.sleep_time_app_load
    return 1.0  # Default value

def sleep_time_in_app_load():
    if hw_manager and hw_manager.sleep_time_in_app_load:
        return hw_manager.sleep_time_in_app_load
    return 0.5  # Default value



def helloworld():
    hw_manager.delay_before_print("It works!!!", 'in_app')

def nameO():
    print("Opti P3", op3vIST)


def create_template(template_name):
    template_content = f"""\

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    programs_dir = os.path.join(os.path.dirname(__file__), "programs")
    os.makedirs(programs_dir, exist_ok=True)
    template_file_path = os.path.join(programs_dir, f"{template_name}.py")
    with open(template_file_path, 'w') as f:
        f.write(template_content)

    print(f"Template file '{template_file_path}' created successfully.")

def rmdir(folder_name):
    try:
        dir_path = os.path.join(current_directory, folder_name)
        if os.path.exists(dir_path):
            if not os.listdir(dir_path):  # Check if directory is empty
                os.rmdir(dir_path)
                print(f"Removed directory: {folder_name}")
            else:
                print(f"Error: Directory not empty - {folder_name}")
        else:
            print(f"Directory not found: {folder_name}")
    except Exception as e:
        print(f"Error removing directory: {str(e)}")

def delete_file(file_name):
    try:
        file_path = os.path.join(current_directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_name}")
        elif os.path.isdir(file_path):
            print(f"Error: '{file_name}' is a directory (use 'rmdir')")
        else:
            print(f"File not found: {file_name}")
    except PermissionError:
        print(f"Error: Permission denied for '{file_name}'")
    except Exception as e:
        print(f"Error deleting file: {str(e)}")

def main():
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
        'bios': bios,
        'computername': hw_manager.computername,
        'autostart': hw_manager.autostart,
        'name': hw_manager.nameO,
        'cls': cls,
        'clear': cls,
        'manage_extensions': manage_extensions,
        'exit': lambda: exit(0),
        'reboot': lambda: [print("Rebooting..."), time.sleep(1), main()],
        'shutdown': lambda: [print("Shutting down..."), time.sleep(1), exit(0)],
        'dir': ls,
        'ls': ls,
        'cd': cd,
        'mkdir': mkdir,
        'touch': touch,
        'rmdir': rmdir,
        'deldir': rmdir,
        'root': root,
        'config': hw_manager.config_editor,
        'configure': hw_manager.config_editor,
        'settings': hw_manager.config_editor,
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
        relative_path = os.path.relpath(current_directory, initial_directory)
        if relative_path == ".":
            relative_path = ""
        prompt = f"O:/{relative_path}> " if relative_path else "O:/> "
        
        try:
            inp = input(prompt).strip()
            if not inp:
                continue
                
            parts = inp.split()
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if cmd in ('del', 'delete', 'rm'):
                if args:
                    delete_file(args[0])
                else:
                    print("Error: Missing filename (usage: del <filename>)")
                continue
                
            if cmd in command_mappings:
                if cmd in ('cd', 'mkdir', 'touch', 'rmdir') and args:
                    command_mappings[cmd](args[0])
                else:
                    command_mappings[cmd]()
            elif cmd in extensions:
                try:
                    extensions[cmd](*args)
                except Exception as e:
                    print(f"Error executing plugin command: {str(e)}")

            elif cmd == 'run' and args:
                file_name = args[0]
                program_path = os.path.join(current_directory, file_name)
                if os.path.exists(program_path):
                    try:
                        subprocess.run([sys.executable, program_path])
                    except Exception as e:
                        print(f"Error running program: {str(e)}")
                else:
                    print(f"Program not found: {file_name}")

            elif cmd == 'create-template' and args:
                create_template(args[0])

            else:
                print(f"Unknown command: {cmd}")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' or 'shutdown' to quit")
        except Exception as e:
            print(f"Error: {str(e)}")

def ls():
    """List directory contents"""
    try:
        print(f"\nDirectory of O:/{os.path.relpath(current_directory, initial_directory) or 'root'}\n")
        print(f"{'Type':<8} {'Name':<20} {'Size':>10}")
        print("-" * 40)
        
        for item in sorted(os.listdir(current_directory)):
            full_path = os.path.join(current_directory, item)
            if os.path.isdir(full_path):
                print(f"{'<DIR>':<8} {item:<20} {'':>10}")

        for item in sorted(os.listdir(current_directory)):
            full_path = os.path.join(current_directory, item)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path)
                print(f"{'':<8} {item:<20} {size:>10,}")
                
        print()
    except Exception as e:
        print(f"Error listing directory: {str(e)}")

def cd(folder_name):
    global current_directory
    
    if folder_name == "..":
        if current_directory != initial_directory:
            current_directory = os.path.dirname(current_directory)
        return
    elif folder_name == ".":
        return
    elif folder_name.lower() == "root":
        current_directory = initial_directory
        return
    
    new_path = os.path.join(current_directory, folder_name)
    if os.path.isdir(new_path):
        current_directory = new_path
    else:
        print(f"Directory not found: {folder_name}")

def mkdir(folder_name):
    try:
        new_path = os.path.join(current_directory, folder_name)
        os.makedirs(new_path, exist_ok=True)
        print(f"Created directory: {folder_name}")
    except Exception as e:
        print(f"Error creating directory: {str(e)}")

def touch(file_name):
    try:
        new_path = os.path.join(current_directory, file_name)
        with open(new_path, 'w'):
            pass
        print(f"Created file: {file_name}")
    except Exception as e:
        print(f"Error creating file: {str(e)}")

def root():
    global current_directory
    current_directory = initial_directory
    print("Returned to root directory")

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
        if mb:
            create_floppy_drives(mb)

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
            cwd=os.getcwd()  # Force run from project root!
        )
    except subprocess.CalledProcessError as e:
        print(f"BIOS execution failed with return code {e.returncode}")
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
