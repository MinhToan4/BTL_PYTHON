"""
Tổng quan về file keyinput.py:

File keyinput.py cung cấp functions để simulate nhấn và thả phím trên Windows sử dụng ctypes.
Được sử dụng để điều khiển xe bằng cách gửi key events trực tiếp đến hệ thống.
"""

import ctypes

# Dictionary mapping key names to scan codes
keys = {
    "w":0x11,  # Scan code cho phím W
    "a":0x1E,  # Scan code cho phím A
    "s":0x1F,  # Scan code cho phím S
    "d":0x20,  # Scan code cho phím D
}

# Định nghĩa structures cho Windows API SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    """
    Structure cho keyboard input.
    """
    _fields_ = [("wVk", ctypes.c_ushort),      # Virtual key code
                ("wScan", ctypes.c_ushort),    # Scan code
                ("dwFlags", ctypes.c_ulong),   # Flags
                ("time", ctypes.c_ulong),      # Timestamp
                ("dwExtraInfo", PUL)]          # Extra info

class HardwareInput(ctypes.Structure):
    """
    Structure cho hardware input.
    """
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    """
    Structure cho mouse input.
    """
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    """
    Union chứa các loại input.
    """
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    """
    Main Input structure.
    """
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def press_key(key):
    """
    Simulate nhấn phím.
    
    Args:
        key (str): Tên phím ('w', 'a', 's', 'd')
    """
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, keys[key], 0x0008, 0, ctypes.pointer(extra) )  # KEYEVENTF_SCANCODE
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(key):
    """
    Simulate thả phím.
    
    Args:
        key (str): Tên phím ('w', 'a', 's', 'd')
    """
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, keys[key], 0x0008 | 0x0002, 0, ctypes.pointer(extra) )  # KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))