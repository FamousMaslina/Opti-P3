import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import op3  # use the already-loaded HardwareManager + helpers


def kv(k, v):
    print(f"  {k:<22} {v}")


def section(title):
    print(title)
    print("-" * len(title))


def main():
    op3.init_hw()
    hm = op3.hw_manager

    cpu     = hm.get_component('cpu')
    mb      = hm.get_component('mb')
    mon     = hm.get_component('mon')
    flo     = hm.get_component('flo')
    hd      = hm.get_component('hd')          # not used directly; we list IDE ports
    gpu     = hm.get_component('gpu')
    modem   = hm.get_component('modem')
    sound   = hm.get_component('sound')
    battery = hm.get_component('battery')
    laptop  = hm.get_component('laptop')
    op3.clear()
    print(f"{op3.osName} Device Manager")
    op3.linebr(40)
    kv("Version", op3.op3vIST)
    kv("Computer Name", hm.config.get('user', 'computer_name', fallback='DEFAULT'))


    section("Motherboard")
    if mb:
        kv("Model", getattr(mb, 'mbName', 'Unknown'))
        kv("Memory", getattr(mb, 'mbMemSTR', 'Unknown'))
    else:
        print("  (no motherboard module loaded)")
    print()

    section("Processor")
    if cpu:
        kv("CPU", getattr(cpu, 'cName', 'Unknown'))
        speed = f"{getattr(cpu, 'cFreqS', '?')}{getattr(cpu, 'cFreqUnit', 'MHz')}"
        kv("Speed", speed)
    else:
        print("  (no CPU detected)")
    print()

    section("Storage Devices")
    drives = op3._extract_ide_drives(mb)
    if drives:
        for i, (name, size) in enumerate(drives, 1):
            kv(f"Drive {i}", f"{name} — {size}")
    else:
        print("  No IDE storage detected")
    print()

    section("Floppy Controller")
    if flo:
        kv("Controller", getattr(flo, 'flo1name', getattr(flo, 'floname', 'FDC')))
    else:
        print("  (none)")
    print()

    section("Graphics")
    if gpu:
        kv("Adapter", getattr(gpu, 'gName', 'Unknown'))
        kv("VRAM", f"{getattr(gpu, 'gVram', '?')} MB")
        kv("Core Clock", f"{getattr(gpu, 'gSpeed', '?')} MHz")
        kv("Pixel Shaders", getattr(gpu, 'gps', '?'))
        kv("Vertex Shaders", getattr(gpu, 'gvs', '?'))
        kv("ROPs", getattr(gpu, 'grop', '?'))
    else:
        print("  (none)")
    print()

    section("Sound")
    if sound:
        kv("Card", getattr(sound, 'soundName', 'Unknown'))
        kv("Chip", getattr(sound, 'soundChip', 'Unknown'))
        kv("Format", getattr(sound, 'soundDF', 'Unknown'))
        kv("Stereo", "Yes" if getattr(sound, 'stereo', False) else "No")
    else:
        print("  (none)")
    print()

    section("Networking / Modem")
    if modem:
        kv("Modem", getattr(modem, 'modemname', 'Unknown'))
        kv("Dial-up Adapter", getattr(modem, 'dialupadp', 'Unknown'))
        kv("Speeds", getattr(modem, 'modemspeeds', 'Unknown'))
    else:
        print("  (none)")
    print()

    section("Display")
    if mon:
        name = getattr(mon, 'monitorName', None)
        mid  = getattr(mon, 'monitorID', None)
        res  = getattr(mon, 'monitorRes', None)
        hz   = getattr(mon, 'monitorHz', None)
        if name: kv("Monitor", name)
        if mid:  kv("ID", mid)
        if res or hz: kv("Mode", f"{res or '?'} @ {hz or '?'}")
        if not any([name, mid, res, hz]):
            print("  (module present, no attributes exposed)")
    else:
        print("  (none)")
    print()

    section("Battery / Laptop")
    any_power = False
    if laptop:
        any_power = True
        kv("Model", getattr(laptop, 'laptopModel', 'Unknown'))
        kv("OEM", getattr(laptop, 'laptopOEM', 'Unknown'))
        kv("Screen", f"{getattr(laptop, 'screenSize', '?')}\"")
    if battery:
        any_power = True
        kv("Type", getattr(battery, 'batteryType', 'Unknown'))
        kv("Capacity", f"{getattr(battery, 'batteryCapacity', '?')} mAh")
        kv("Charge", f"{getattr(battery, 'currentCharge', '?')}%")
    if not any_power:
        print("  (none)")
    print()


if __name__ == "__main__":
    main()
