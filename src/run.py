from modules.common.map import Map
from modules.common.path import Path
from modules.common.point import Point
from modules.custers import run, get_clusters_from_ids, get_all_points_in_clusters
from modules.visualizer import visualize
from modules.path_finding import PathFinding

if __name__ == "__main__":
    map = Map.load_from_file("data/data.txt", 100)
    start = map.points[0]
    end = map.points[123]

    map_size = 10000
    cluster_size = 100

    k = 100

    clusters, selected_clusters = run(map.points, start, end, cluster_size=cluster_size, map_size=map_size, k=k)

    points = get_all_points_in_clusters(
        get_clusters_from_ids(clusters, selected_clusters)
    )

    pf = PathFinding(points, start, end, k=k)
    path = pf.aco_path(num_ants=100, num_iterations=10, alpha=1, beta=3, evaporation_rate=0.9, pheromone_deposit=20  )
    # path = pf.greedy_path()

    print(f"\nPath length: {round(path.distance() / 100, 2)}")
    print(f"Points in path: {len(path.points)}")
    visualize(map.points, clusters, selected_clusters, cluster_size=cluster_size, map_size=map_size, path=path, draw_clusters=True, draw_points=True)