from math import sqrt
import random
import time
import ctypes
import numpy as np
import platform 
import pathlib 

# Globalna flaga do kontroli implementacji
USE_C_IMPLEMENTATION = True

from modules.common.path import Path
from modules.common.point import Point
from modules.custers import get_all_points_in_clusters

class PathFinding:
    def __init__(self, points: list[Point], start: Point, end: Point, k: int = 100):
        # Deklaracja global na początku funkcji
        global USE_C_IMPLEMENTATION
        
        self.points = points
        self.start = start
        self.end = end
        self.k = k
        
        # Ładowanie biblioteki C dla ACO
        if USE_C_IMPLEMENTATION:
            try:
                current_dir = pathlib.Path(__file__).parent.resolve()
                # Poprawiona ścieżka - przejdź do folderu common/c_modules
                lib_path = str(current_dir / 'c_modules' / ('aco_probability.dll' if platform.system() == "Windows" else 'aco_probability.so'))
                
                self._aco_lib = ctypes.CDLL(lib_path)
                self._aco_lib.calculate_probabilities.argtypes = [
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_int,
                    ctypes.c_double,
                    ctypes.c_double
                ]
                print(f"[C] Loaded ACO library: {lib_path}")
            except Exception as e:
                print(f"[C] Error loading ACO library: {e}")
                USE_C_IMPLEMENTATION = False

    def greedy_path(self) -> Path:
        start_time = time.time()

        if self.k < 2:
            raise ValueError("k must be at least 2 (start and end)")

        candidates = [p for p in self.points if p != self.start and p != self.end]

        def bias(p: Point) -> float:
            return Point.distance(self.start, p) + Point.distance(p, self.end)

        candidates.sort(key=bias)
        selected = candidates[:self.k - 2]

        unvisited = set(selected)
        path_points = [self.start]
        current = self.start

        while unvisited:
            next_point = min(unvisited, key=lambda p: Point.distance(current, p))
            path_points.append(next_point)
            unvisited.remove(next_point)
            current = next_point

        path_points.append(self.end)

        best_path = Path(self.start, self.end, path_points)
        total_time = time.time() - start_time
        print(f"\n[GREEDY] Total time: {total_time:.2f} seconds")
        print(f"[GREEDY] Best path: {round(best_path.distance() / 100, 2)} m\n")
        return best_path

    def aco_path(
        self,
        num_ants: int = 20,
        num_iterations: int = 100,
        alpha: float = 1.0,
        beta: float = 5.0,
        evaporation_rate: float = 0.5,
        pheromone_deposit: float = 100.0,
    ) -> Path:
        
        start_time = time.time()

        candidates = [p for p in self.points if p != self.start and p != self.end]

        if len(candidates) < self.k:
            raise ValueError(f"Not enough intermediate points ({len(candidates)}) for k={self.k}")

        # Initial greedy path to get starting solution
        greedy_solution = self.greedy_path()
        greedy_points = greedy_solution.points

        # Initialize pheromones
        all_points = [self.start] + candidates + [self.end]
        pheromones = {(a, b): 100.0 for a in all_points for b in all_points if a != b}

        # Boost pheromones on greedy path edges
        for i in range(min(len(greedy_points) - 1, self.k + 1)):
            a, b = greedy_points[i], greedy_points[i + 1]
            pheromones[(a, b)] += pheromone_deposit
            pheromones[(b, a)] += pheromone_deposit

        best_path = None
        best_length = float('inf')

        for iteration in range(num_iterations):
            all_paths = []

            for ant in range(num_ants):
                path = [self.start]
                current = self.start
                unvisited = set(candidates)

                # Select exactly k intermediate points
                for _ in range(self.k):
                    if not unvisited:
                        break
                        
                    # Prepare data for C function
                    candidate_list = list(unvisited)
                    n = len(candidate_list)
                    
                    pheromones_arr = np.zeros(n, dtype=np.float64)
                    distances_arr = np.zeros(n, dtype=np.float64)
                    
                    for i, point in enumerate(candidate_list):
                        pheromones_arr[i] = pheromones[(current, point)]
                        distances_arr[i] = Point.distance(current, point)

                    if USE_C_IMPLEMENTATION:
                        probabilities = self._calculate_probabilities_c(
                            pheromones_arr, 
                            distances_arr, 
                            alpha, 
                            beta
                        )
                        # Ustaw total_prob dla bezpieczeństwa
                        total_prob = 1.0
                    else:
                        # Oryginalna implementacja Python
                        probabilities = []
                        total_prob = 0.0
                        
                        for i, point in enumerate(candidate_list):
                            tau = pheromones_arr[i]
                            dist = distances_arr[i]
                            eta = 1.0 / (dist + 1e-6)
                            prob = (tau ** alpha) * (eta ** beta)
                            probabilities.append(prob)
                            total_prob += prob
                        
                        if total_prob > 0:
                            probabilities = [p / total_prob for p in probabilities]
                        else:
                            probabilities = [1.0 / n] * n

                    # Wybór następnego punktu
                    if total_prob > 0:
                        r = random.random()
                        cumulative = 0.0
                        for i, point in enumerate(candidate_list):
                            cumulative += probabilities[i]
                            if r <= cumulative:
                                next_point = point
                                break
                    else:
                        next_point = random.choice(candidate_list)

                    path.append(next_point)
                    unvisited.remove(next_point)
                    current = next_point

                # Add end point
                path.append(self.end)

                # Calculate path length
                length = sum(Point.distance(path[i], path[i + 1]) for i in range(len(path) - 1))
                all_paths.append((path, length))

                if length < best_length:
                    best_length = length
                    best_path = path
                    print(f"[ACO] Iteration {iteration}, Ant {ant}: New best length = {best_length:.2f}")

            # Evaporate pheromones
            for key in pheromones:
                pheromones[key] *= (1 - evaporation_rate)

            # Deposit pheromones
            for path, length in all_paths:
                deposit = pheromone_deposit / (length + 1e-6)
                for i in range(len(path) - 1):
                    a, b = path[i], path[i + 1]
                    pheromones[(a, b)] += deposit
                    pheromones[(b, a)] += deposit

        best_path = Path(self.start, self.end, best_path)
        total_time = time.time() - start_time
        print(f"\n[ACO] Total time: {total_time:.2f} seconds")
        print(f"[ACO] Best path: {round(best_path.distance() / 100, 2)} m")
        return best_path

    def _calculate_probabilities_c(self, pheromones, distances, alpha, beta):
        """Wywołanie funkcji C do obliczenia prawdopodobieństw"""
        n = len(pheromones)
        probs = np.zeros(n, dtype=np.float64)
        
        self._aco_lib.calculate_probabilities(
            probs.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            pheromones.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            distances.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            n,
            ctypes.c_double(alpha),
            ctypes.c_double(beta)
        )
        return probs