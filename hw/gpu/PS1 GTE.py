gName = "Sony CXD8514Q"
gSpeed = 34
gSpeedS = "34 MHz"
gps = 2
gvs = 1
grop = 1
gVram = 1
gbit = "16 Bits"
odasfsdfds3 = True
import time
from os import *
ver = 1.0
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def shadowgpu():
    clear()
    print(gName, "VGA BIOS.", ver)
    print(gVram, "MB loaded.")
    time.sleep(0.7)
