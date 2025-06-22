from modules.common.point import Point

class Path:
    def __init__(self, start: Point, end: Point, points: list[Point]):
        self.start = start
        self.end = end
        self.points = points

    def distance(self) -> float:
        dist = 0
        for i in range(len(self.points) - 1):
            dist += Point.distance(self.points[i], self.points[i + 1])
        return dist