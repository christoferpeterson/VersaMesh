import os
import platform

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
    
def is_macos():
    return platform.system() == "Darwin"

def is_windows():
    return os.name == 'nt'