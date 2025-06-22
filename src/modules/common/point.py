# point.py (zmodyfikowany)
from math import sqrt, pow
import ctypes
import os
import pathlib
import platform 

USE_C_IMPLEMENTATION = True 

try:
    if USE_C_IMPLEMENTATION:
        current_dir = pathlib.Path(__file__).parent.resolve()
        # Poprawiona ścieżka - przejdź do folderu common/c_modules
        lib_path = str(current_dir / 'c_modules' / ('distance.dll' if platform.system() == "Windows" else 'distance.so'))
        
        distance_lib = ctypes.CDLL(lib_path)
        distance_lib.point_distance.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        distance_lib.point_distance.restype = ctypes.c_double
        print(f"Successfully loaded C distance library: {lib_path}")
except Exception as e:
    print(f"Error loading C distance library: {e}")
    USE_C_IMPLEMENTATION = False

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @staticmethod
    def distance(p1: 'Point', p2: 'Point') -> float:
        # Wybór implementacji: oryginalna Python lub nowa C
        if USE_C_IMPLEMENTATION:  # Globalna flaga konfiguracyjna
            return distance_lib.point_distance(p1.x, p1.y, p2.x, p2.y)
        else:
            # Oryginalna implementacja Python
            return sqrt(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2))