import os
import re
import sys
import time
from importlib import import_module
from os import name, system
op3vIST = "0.1"
op3vIINT = 0.1
def cls():
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
        self.hw_dir = os.path.join(os.getcwd(), "hw")
        sys.path.append(self.hw_dir)
        self.initialize_hardware()

        # Initialize CPU timing variables
        self.delay_app = 1.0  # Default values
        self.delay_in_app = 0.5
        self.init_cpu_timing()

    def init_cpu_timing(self):
        """Initialize CPU frequency-based timing"""
        if 'cpu' in self.loaded_modules:
            cpu = self.loaded_modules['cpu']
            try:
                # Calculate delays based on CPU frequency
                self.delay_app = 45 / cpu.cFreq
                self.delay_in_app = 15 / cpu.cFreq
            except AttributeError:
                print("Warning: CPU frequency not properly configured")
                # Fall back to defaults if CPU info missing

    def delay_before_print(self, delay_type='app'):
        """
        Wait for appropriate time before printing
        delay_type: 'app' for application load, 'in_app' for in-application
        """
        delay = self.delay_in_app if delay_type == 'in_app' else self.delay_app
        time.sleep(delay)

    def scan_for_hardware(self):
        """Precise hardware scanning with strict type checking"""
        print("\nScanning hardware directory...")
        hw_files = [f for f in os.listdir(self.hw_dir) if f.endswith('.py') and not f.startswith('id')]
        
        for file in hw_files:
            try:
                with open(os.path.join(self.hw_dir, file), 'r') as f:
                    content = f.read()
                    
                    # Skip BIOS file explicitly
                    if file.lower() == 'bios.py':
                        continue
                        
                    # CPU detection (strict requirements)
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
        """Create ID file for detected hardware"""
        with open(os.path.join(self.hw_dir, f"id{hw_type}.py"), 'w') as f:
            f.write(f"{hw_type} = '{filename}'")
        self.hardware[hw_type] = filename

    def initialize_hardware(self):
        """Initialize all hardware components"""
        print("\nInitializing hardware...")
        
        # First scan and create ID files
        self.scan_for_hardware()
        
        # Then load existing ID files
        self.load_id_files()
        self.import_hardware_modules()
        self.check_essential_components()

    def load_id_files(self):
        """Load hardware identification files"""
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
        """Import hardware modules with strict validation"""
        print("\nImporting hardware modules...")
        for hw_type, hw_file in self.hardware.items():
            if hw_file and hw_file.lower() != 'bios.py':  # Skip BIOS file
                try:
                    module_name = hw_file.replace('.py', '')
                    module = import_module(f"hw.{module_name}")
                    
                    # Validate module contents based on type
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
                    # Clean up invalid ID file
                    id_file = os.path.join(self.hw_dir, f"id{hw_type}.py")
                    if os.path.exists(id_file):
                        os.remove(id_file)

    def check_essential_components(self):
        """Check for essential components"""
        print("\nVerifying essential components...")
        if 'cpu' not in self.loaded_modules:
            print(" !!! ERROR: No valid CPU detected - system cannot boot !!!")
        if 'mb' not in self.loaded_modules:
            print(" !!! WARNING: No valid motherboard detected - limited functionality !!!")

    def get_component(self, name):
        """Safe access to hardware components"""
        return self.loaded_modules.get(name)

# Global hardware manager
hw_manager = None

def init_hw():
    global hw_manager
    hw_manager = HardwareManager()
    
    # Display hardware summary
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
    """Calculate application load time based on CPU frequency"""
    if hw_manager and hw_manager.sleep_time_app_load:
        return hw_manager.sleep_time_app_load
    return 1.0  # Default value

def sleep_time_in_app_load():
    """Calculate in-application load time based on CPU frequency"""
    if hw_manager and hw_manager.sleep_time_in_app_load:
        return hw_manager.sleep_time_in_app_load
    return 0.5  # Default value

def helloworld():
    hw_manager.delay_before_print("It works!!!", 'in_app')
def nameO():
    print("Opti P3", op3vIST)
def main():
    cls()
    nameO()
    while True:
        inp = input("O:/ ") 
        inp = inp.lower()
        if inp in ('helloworld'):
            eval(inp)()    

def mainBoot():
    cpu = hw_manager.get_component('cpu')
    mb = hw_manager.get_component('mb')
    
    if not cpu:
        print("\nBOOT FAILED: Essential hardware missing (CPU)")
        return
    
    hw_manager.delay_before_print('app')
    print("\nSystem booting...")
    
    try:
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

    


if __name__ == "__main__":
    # Ensure hw directory exists
    if not os.path.exists("hw"):
        os.makedirs("hw")
        print("Created hw directory")
    cls()
    init_hw()
    mainBoot()