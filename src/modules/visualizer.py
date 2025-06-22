import tkinter as tk
from modules.common.point import Point
from modules.common.path import Path

def visualize(points: list[Point], 
                               clusters: list[list[Point]], 
                               selected_clusters: list[int],
                               cluster_size: int, 
                               map_size: int,
                               path: Path = None,
                               draw_clusters: bool = True, draw_points: bool = True):
    """
    Visualizes clusters, points, and optionally a path on a Tkinter canvas.
    
    - `points`: All points to be drawn.
    - `clusters`: A 2D array (list of lists) where each sublist is a cluster of points.
    - `clusters_between`: A list of cluster indices that should be highlighted (non-empty clusters within the selection bounds).
    - `cluster_size`: The size (in map units) of one cluster cell.
    - `map_size`: Overall map size.
    - `path`: An optional Path instance containing a start, end, and path (ordered points).
    """
    grid_size = map_size // cluster_size
    canvas_size = 800
    scale = canvas_size / map_size

    root = tk.Tk()
    root.title("Cluster Visualization")

    canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="white")
    canvas.pack()

    # Draw cluster grid
    if draw_clusters:
        for y in range(grid_size):
            for x in range(grid_size):
                cluster_id = y * grid_size + x
                x0 = x * cluster_size * scale
                y0 = y * cluster_size * scale
                x1 = x0 + cluster_size * scale
                y1 = y0 + cluster_size * scale

                # Only fill clusters if their index appears in clusters_between
                fill = "lightblue" if cluster_id in selected_clusters else ""
                canvas.create_rectangle(x0, y0, x1, y1, outline="gray", fill=fill)

    # Draw all points (small black dots)
    if draw_points:
        for point in points:
            px = point.x * scale
            py = point.y * scale
            canvas.create_oval(px - 1, py - 1, px + 1, py + 1, fill="gray")

    # Draw path if provided
    if path is not None and len(path.points) > 1:
        # Draw blue line between consecutive points in the path
        for i in range(len(path.points) - 1):
            p1 = path.points[i]
            p2 = path.points[i + 1]
            canvas.create_line(p1.x * scale, p1.y * scale, p2.x * scale, p2.y * scale,
                               fill="blue", width=2)
        # Highlight the start and end points of the path
        sx, sy = path.start.x * scale, path.start.y * scale
        ex, ey = path.end.x * scale, path.end.y * scale
        canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, fill="green")
        canvas.create_oval(ex - 5, ey - 5, ex + 5, ey + 5, fill="red")

    root.mainloop()
