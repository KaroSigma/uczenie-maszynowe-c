import os

from modules.common.point import Point
from modules.common.path import Path

class Map:
    def __init__(self, name: str, points: list[Point] = None):
        self.name = name
        self.points = points if points is not None else []
    
    def save_to_file(self, directory: str = "data"):
        """
        Saves the list of points to a file in the given directory.
        Format: x % y per line.
        """
        filepath = os.path.join(directory, f"{self.name}.txt")
        with open(filepath, "w") as file:
            file.writelines([f"{point.x} % {point.y}\n" for point in self.points])

    @staticmethod
    def load_from_file(filepath: str, scale = 1) -> 'Map':
        """
        Loads a map from a file and returns a Map instance.
        """
        points = []

        with open(filepath, 'r') as file:
            for line in file:
                try:
                    x_str, y_str = line.split(" % ")
                    if scale == 1:
                        points.append(Point(int(x_str), int(y_str)))
                    else:
                        x = int(float(x_str) * 100)
                        y = int(float(y_str) * 100)
                        points.append(Point(x, y))
                except ValueError:
                    continue
        
        name = os.path.splitext(os.path.basename(filepath))[0]
        return Map(name, points)
