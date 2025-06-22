import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Parametry symulacji
AREA_SIZE = 50  # m
HOME = (25, 25)
VELOCITY = 0.1  # m/s
MAX_TIME = 7200  # s (2 godziny)
MAX_OBJECTS = 5  # max obiektów w pyszczku

# Dane obiektów
OBJECTS_COUNT = {
    'mysz_polna': 150,
    'mysz_domowa': 80,
    'slimak': 90,
    'lisc': 300,
    'kamyk': 200
}

# Czas polowania (s)
HUNTING_TIME = {
    'mysz_polna': 180,
    'mysz_domowa': 120,
    'slimak': 90,
    'lisc': 60,
    'kamyk': 30
}

# Wartości obiektów dla kotów
VALUES = {
    'Ariana': {
        'mysz_polna': 10, 'mysz_domowa': 8, 'slimak': 5, 'lisc': 1, 'kamyk': 0
    },
    'Luna': {
        'mysz_polna': 0, 'mysz_domowa': 0, 'slimak': 7, 'lisc': 3, 'kamyk': 2
    },
    'Dante': {
        'mysz_polna': 0, 'mysz_domowa': 6, 'slimak': 0, 'lisc': 4, 'kamyk': 3
    }
}

# Kolory obiektów i tras
OBJECT_COLORS = {
    'mysz_polna': 'brown',
    'mysz_domowa': 'gray',
    'slimak': 'green',
    'lisc': 'lightgreen',
    'kamyk': 'black'
}

CAT_COLORS = {
    'Ariana': 'red',
    'Luna': 'blue',
    'Dante': 'purple'
}

# Generowanie obiektów
def generate_objects():
    objects = []
    for obj_type, count in OBJECTS_COUNT.items():
        for _ in range(count):
            x = np.random.uniform(0, AREA_SIZE)
            y = np.random.uniform(0, AREA_SIZE)
            objects.append({'type': obj_type, 'position': (x, y)})
    return objects

# Odległość euklidesowa
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Symulacja polowania dla jednego kota
def simulate_hunt(cat, available_objects):
    current_pos = HOME
    carried_objects = 0
    time_used = 0
    path = [HOME]
    collected = []
    
    while time_used < MAX_TIME:
        # Filtruj obiekty o dodatniej wartości dla kota
        candidates = [obj for obj in available_objects if VALUES[cat][obj['type']] > 0]
        if not candidates:
            break
            
        # Oblicz odległości i posortuj (optymalizacja: 50 najbliższych)
        candidates_with_dist = [(obj, distance(current_pos, obj['position'])) for obj in candidates]
        candidates_with_dist.sort(key=lambda x: x[1])
        candidates_subset = candidates_with_dist[:50]
        
        best_obj = None
        best_ratio = -np.inf
        return_home = False
        
        for obj, dist in candidates_subset:
            # Czas dojścia do obiektu
            time_to_obj = dist / VELOCITY
            # Czas polowania
            hunt_time = HUNTING_TIME[obj['type']]
            # Jeśli po zebraniu kot będzie miał 5 obiektów, dodaj czas powrotu do domu
            if carried_objects + 1 == MAX_OBJECTS:
                time_to_home = distance(obj['position'], HOME) / VELOCITY
                total_time = time_to_obj + hunt_time + time_to_home
            else:
                total_time = time_to_obj + hunt_time
            
            # Sprawdź, czy starczy czasu
            if time_used + total_time > MAX_TIME:
                continue
                
            # Wartość na jednostkę czasu
            value = VALUES[cat][obj['type']]
            ratio = value / total_time
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_obj = obj
                best_total_time = total_time
                return_home = (carried_objects + 1 == MAX_OBJECTS)
        
        if best_obj is None:
            break
            
        # Zbierz obiekt
        time_used += best_total_time
        collected.append(best_obj)
        available_objects.remove(best_obj)
        carried_objects += 1
        path.append(best_obj['position'])
        
        # Wróć do domu po 5. obiekt
        if return_home:
            path.append(HOME)
            current_pos = HOME
            carried_objects = 0
        else:
            current_pos = best_obj['position']
    
    return {
        'collected': collected,
        'path': path,
        'time_used': time_used
    }

# Główna symulacja
def main():
    # Inicjalizacja
    all_objects = generate_objects()
    cats = ['Ariana', 'Luna', 'Dante']
    results = {}
    available_objects = all_objects.copy()
    
    # Symuluj polowanie dla każdego kota
    for cat in cats:
        results[cat] = simulate_hunt(cat, available_objects)
        print(f"{cat}: zebrano {len(results[cat]['collected'])} obiektów, czas: {results[cat]['time_used']} s")
    
    # Wizualizacja
    plt.figure(figsize=(12, 12))
    
    # Rysuj pozostałe obiekty
    for obj in available_objects:
        x, y = obj['position']
        plt.scatter(x, y, color=OBJECT_COLORS[obj['type']], s=20, alpha=0.7)
    
    # Rysuj trasy kotów
    for cat in cats:
        path = results[cat]['path']
        x, y = zip(*path)
        plt.plot(x, y, color=CAT_COLORS[cat], linewidth=2, marker='o', markersize=4, label=cat)
        plt.scatter(x[0], y[0], color='black', s=200, zorder=5)  # dom
    
    # Legenda
    legend_elements = []
    for obj_type, color in OBJECT_COLORS.items():
        legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=obj_type))
    for cat, color in CAT_COLORS.items():
        legend_elements.append(Line2D([0], [0], color=color, linewidth=2, label=f'Trasa {cat}'))
    legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=10, label='Dom'))
    
    plt.legend(handles=legend_elements, loc='upper right')
    plt.title('Trasy polowań kotów')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.xlim(0, AREA_SIZE)
    plt.ylim(0, AREA_SIZE)
    plt.grid(alpha=0.3)
    plt.savefig('hunting_paths.png')
    plt.show()

if __name__ == "__main__":
    main()