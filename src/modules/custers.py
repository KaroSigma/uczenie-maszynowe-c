from modules.common.point import Point
from modules.common.path import Path

from math import sqrt


def create_clusters(points: list[Point], cluster_size: int, map_size: int) -> list[list[Point]]:
    clusters_count = map_size // cluster_size * map_size // cluster_size
    clusters = [[] for _ in range(clusters_count)]

    for point in points:
        x = point.x // cluster_size
        y = point.y // cluster_size
        cluster_id = int(y * sqrt(clusters_count) + x)
        try:
            clusters[cluster_id].append(point)
        except IndexError:
            print(f"[IndexError] x: {x} y: {y}\tCluster id: {cluster_id}")
    
    return clusters


def get_cluster_ids_in_square_between_points(clusters: list[list[Point]], 
                                             p1: Point, p2: Point, 
                                             cluster_size: int, map_size: int,
                                             k: int) -> list[int]:
    grid_size = map_size // cluster_size

    # Get grid coordinates for p1 and p2
    x1, y1 = p1.x // cluster_size, p1.y // cluster_size
    x2, y2 = p2.x // cluster_size, p2.y // cluster_size

    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)

    cluster_ids = []

    while True:
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if x >= grid_size or y >= grid_size:
                    continue  # skip out-of-bounds

                cluster_id = y * grid_size + x
                if clusters[cluster_id]:  # not empty
                    cluster_ids.append(cluster_id)

        if len(get_all_points_in_clusters(get_clusters_from_ids(clusters, cluster_ids))) >= k:
            break
        min_x -= 1
        min_y -= 1
        max_x += 1
        max_y += 1

    return cluster_ids



def get_clusters_from_ids(clusters: list[list[Point]], ids: list[int]) -> list[list[Point]]:
    temp = []
    for i, cluster in enumerate(clusters):
        if i in ids:
            temp.append(cluster)
    return temp

def get_all_points_in_clusters(clusters: list[list[Point]]) -> list[Point]:
    points = []
    for cluster in clusters:
        for point in cluster:
            points.append(point)
    return points
    

def run(points: list[Point], start_point: Point, end_point: Point, cluster_size: int = 100, map_size: int = 5000, k: int = 100
        ) -> tuple[list[list[Point]], list[int]]:
    clusters = create_clusters(points, cluster_size, map_size)
    selected_clusters = get_cluster_ids_in_square_between_points(clusters, start_point, end_point, cluster_size, map_size, k)
    points = get_all_points_in_clusters(get_clusters_from_ids(clusters, selected_clusters))

    print(f"\nCreated {len(clusters)} clusters with size of {cluster_size}")
    print(f"Selected {len(selected_clusters)} clusters")
    print(f"Points in selected clusters: {len(points)}")
    return clusters, selected_clusters