
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
