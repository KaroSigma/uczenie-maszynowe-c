import numpy as np
import matplotlib.pyplot as plt
import heapq
import random
from scipy.ndimage import label
from scipy.spatial.distance import cdist

# Ustawienie ziarna dla reprodukowalności
# np.random.seed(42)
# random.seed(42)

# Parametry terenu
territory_size = 50  # 50x50 jednostek (2500 m²)
n_field_mice = 150
n_house_mice = 80
n_snails = 90
n_leaves = 300
n_rocks = 200

# Generowanie pozycji obiektów (współrzędne ciągłe)
field_mice = np.random.rand(n_field_mice, 2) * territory_size
house_mice = np.random.rand(n_house_mice, 2) * territory_size
snails = np.random.rand(n_snails, 2) * territory_size
leaves = np.random.rand(n_leaves, 2) * territory_size
rocks = np.random.rand(n_rocks, 2) * territory_size

# Tworzenie siatki 50x50
size = 50
n_cells = size * size

# Przypisanie obiektów do komórek siatki
def assign_to_grid(positions, grid_size):
    grid = np.zeros((grid_size, grid_size), dtype=int)
    for pos in positions:
        x, y = pos
        i = min(int(y), grid_size - 1)
        j = min(int(x), grid_size - 1)
        grid[i, j] += 1
    return grid

mice_grid = assign_to_grid(field_mice, size) + assign_to_grid(house_mice, size)
snails_grid = assign_to_grid(snails, size)
leaves_grid = assign_to_grid(leaves, size)
rocks_grid = assign_to_grid(rocks, size)

# Łączenie liści i kamieni dla Dantego
dante_grid = leaves_grid + rocks_grid

# Znajdowanie prostokąta Luny (dotykającego granicy z min. 150 myszami)
rectangles = []

# Górna granica (i1=0)
for i2 in range(size):
    for j1 in range(size):
        for j2 in range(j1, size):
            mice_sum = mice_grid[0:i2+1, j1:j2+1].sum()
            if mice_sum >= 150:
                area = (i2+1) * (j2 - j1 + 1)
                rectangles.append(('top', 0, j1, i2, j2, area, mice_sum))

# Dolna granica (i2=size-1)
for i1 in range(size):
    for j1 in range(size):
        for j2 in range(j1, size):
            mice_sum = mice_grid[i1:size, j1:j2+1].sum()
            if mice_sum >= 150:
                area = (size - i1) * (j2 - j1 + 1)
                rectangles.append(('bottom', i1, j1, size-1, j2, area, mice_sum))

# Lewa granica (j1=0)
for j2 in range(size):
    for i1 in range(size):
        for i2 in range(i1, size):
            mice_sum = mice_grid[i1:i2+1, 0:j2+1].sum()
            if mice_sum >= 150:
                area = (i2 - i1 + 1) * (j2+1)
                rectangles.append(('left', i1, 0, i2, j2, area, mice_sum))

# Prawa granica (j2=size-1)
for j1 in range(size):
    for i1 in range(size):
        for i2 in range(i1, size):
            mice_sum = mice_grid[i1:i2+1, j1:size].sum()
            if mice_sum >= 150:
                area = (i2 - i1 + 1) * (size - j1)
                rectangles.append(('right', i1, j1, i2, size-1, area, mice_sum))

if not rectangles:
    raise RuntimeError("Nie znaleziono odpowiedniego prostokąta dla Luny.")

# Wybór prostokąta o najmniejszym obszarze
rectangles.sort(key=lambda x: (x[5], -x[6]))
border_type, i1, j1, i2, j2, area, mice_sum = rectangles[0]

# Inicjalizacja etykiet regionów
labels = np.zeros((size, size), dtype=int)

# Przypisanie prostokąta Luny
if border_type == 'top':
    labels[0:i2+1, j1:j2+1] = 1
elif border_type == 'bottom':
    labels[i1:size, j1:j2+1] = 1
elif border_type == 'left':
    labels[i1:i2+1, 0:j2+1] = 1
elif border_type == 'right':
    labels[i1:i2+1, j1:size] = 1

# Znajdowanie pozostałych komórek
remaining_indices = np.argwhere(labels == 0)

# Znajdowanie największego spójnego obszaru
remaining_grid = (labels == 0).astype(int)
labeled, num_features = label(remaining_grid)

# Wybór największego spójnego obszaru
largest_component = None
max_size = 0
for i in range(1, num_features + 1):
    component_size = np.sum(labeled == i)
    if component_size > max_size:
        max_size = component_size
        largest_component = (labeled == i)

if largest_component is None:
    raise RuntimeError("Brak spójnego obszaru dla Ariany i Dantego")

# Znajdowanie punktów startowych w odległości od siebie
indices_in_component = np.argwhere(largest_component)

# Wybór punktu startowego Ariany - komórka z największą liczbą ślimaków
seedA = None
max_snails = -1
for idx in indices_in_component:
    i, j = idx
    if snails_grid[i, j] > max_snails:
        max_snails = snails_grid[i, j]
        seedA = (i, j)

# Wybór punktu startowego Dantego - komórka z największą liczbą liści i kamieni, w odległości min. 20 komórek
seedD = None
max_dante = -1
min_distance = 20  # Minimalna odległość między punktami startowymi

for idx in indices_in_component:
    i, j = idx
    dist = np.sqrt((i - seedA[0])**2 + (j - seedA[1])**2)
    if dist >= min_distance and dante_grid[i, j] > max_dante:
        max_dante = dante_grid[i, j]
        seedD = (i, j)

# Jeśli nie znaleziono odpowiedniego punktu dla Dantego, wybierz drugi najlepszy bez ograniczenia odległości
if seedD is None:
    max_dante = -1
    for idx in indices_in_component:
        i, j = idx
        if dante_grid[i, j] > max_dante and (i, j) != seedA:
            max_dante = dante_grid[i, j]
            seedD = (i, j)

# Przypisanie punktów startowych
labels[seedA] = 2
labels[seedD] = 3

# Inicjalizacja kolejek priorytetowych
heapA = []
heapD = []
dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Funkcja dodająca sąsiadów do kolejki
def add_neighbors(heap, cell, grid, labels, region_id):
    i, j = cell
    for di, dj in dirs:
        ni, nj = i + di, j + dj
        if 0 <= ni < size and 0 <= nj < size:
            if largest_component[ni, nj] and labels[ni, nj] == 0:
                heapq.heappush(heap, (-grid[ni, nj], ni, nj))

# Inicjalizacja kolejek
add_neighbors(heapA, seedA, snails_grid, labels, 2)
add_neighbors(heapD, seedD, dante_grid, labels, 3)

# Liczba komórek do przydzielenia w obszarze
total_to_assign = np.sum(largest_component) - 2
assigned_count = 0

# Statystyki regionów
sizeA = 1
sizeD = 1

# Równoważone przydzielanie komórek z uwzględnieniem rozmiaru regionów
while assigned_count < total_to_assign:
    # Wybór regionu do rozszerzenia na podstawie rozmiaru
    if sizeA <= sizeD and heapA:
        # Rozszerzanie regionu Ariany
        neg_val, i, j = heapq.heappop(heapA)
        if labels[i, j] == 0:
            labels[i, j] = 2
            assigned_count += 1
            sizeA += 1
            add_neighbors(heapA, (i, j), snails_grid, labels, 2)
    elif heapD:
        # Rozszerzanie regionu Dantego
        neg_val, i, j = heapq.heappop(heapD)
        if labels[i, j] == 0:
            labels[i, j] = 3
            assigned_count += 1
            sizeD += 1
            add_neighbors(heapD, (i, j), dante_grid, labels, 3)
    
    # Jeśli kolejki są puste, ale są jeszcze komórki do przydzielenia
    if not heapA and not heapD and assigned_count < total_to_assign:
        # Znajdź pierwszą nieprzydzieloną komórkę
        for idx in indices_in_component:
            i, j = idx
            if labels[i, j] == 0:
                # Przydziel do regionu z mniejszą liczbą komórek
                if sizeA <= sizeD:
                    labels[i, j] = 2
                    assigned_count += 1
                    sizeA += 1
                    add_neighbors(heapA, (i, j), snails_grid, labels, 2)
                else:
                    labels[i, j] = 3
                    assigned_count += 1
                    sizeD += 1
                    add_neighbors(heapD, (i, j), dante_grid, labels, 3)
                break

# Tworzenie wizualizacji
plt.figure(figsize=(15, 12))

# 1. Wizualizacja podziału terytorium
color_grid = np.zeros((size, size, 3))
for i in range(size):
    for j in range(size):
        if labels[i, j] == 1:
            color_grid[i, j] = [1, 0, 0]  # Luna - czerwony
        elif labels[i, j] == 2:
            color_grid[i, j] = [0, 1, 0]  # Ariana - zielony
        elif labels[i, j] == 3:
            color_grid[i, j] = [0, 0, 1]  # Dante - niebieski

# Wyświetlenie siatki z przeźroczystością
plt.imshow(color_grid, extent=[0, territory_size, 0, territory_size], 
           origin='lower', alpha=0.3, aspect='auto')

# 2. Dodanie kolorowych kropek reprezentujących obiekty
plt.scatter(field_mice[:, 0], field_mice[:, 1], s=30, c='#2E8B57', alpha=0.8, label='Myszy polne (150)')
plt.scatter(house_mice[:, 0], house_mice[:, 1], s=30, c='#4169E1', alpha=0.8, label='Myszy domowe (80)')
plt.scatter(snails[:, 0], snails[:, 1], s=25, c='#8B4513', alpha=0.7, label='Ślimaki (90)')
plt.scatter(leaves[:, 0], leaves[:, 1], s=15, c='#32CD32', alpha=0.5, label='Liście (300)')
plt.scatter(rocks[:, 0], rocks[:, 1], s=20, c='#708090', alpha=0.6, label='Kamyki (200)')

# 4. Konfiguracja wykresu
plt.title('Zrównoważony podział terytorium dla wszystkich kotów', fontsize=16)
plt.xlabel('X (m)', fontsize=14)
plt.ylabel('Y (m)', fontsize=14)
plt.xticks(np.arange(0, territory_size+1, 5))
plt.yticks(np.arange(0, territory_size+1, 5))
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend(loc='upper right', fontsize=12)

# 5. Dodanie siatki pomocniczej
for x in range(0, territory_size+1, 5):
    plt.axvline(x=x, color='gray', linestyle='--', alpha=0.2)
for y in range(0, territory_size+1, 5):
    plt.axhline(y=y, color='gray', linestyle='--', alpha=0.2)

# 6. Obliczenie i wyświetlenie wyników
luna_mice = np.sum(mice_grid * (labels == 1))
luna_score = luna_mice / 230.0

ariana_snails = np.sum(snails_grid * (labels == 2))
ariana_score = ariana_snails / 90.0

dante_leaves = np.sum(leaves_grid * (labels == 3))
dante_rocks = np.sum(rocks_grid * (labels == 3))
dante_score = (dante_leaves + dante_rocks) / 500.0

# Obliczenie powierzchni regionów
area_luna = np.sum(labels == 1)
area_ariana = np.sum(labels == 2)
area_dante = np.sum(labels == 3)
total_area = size * size

plt.figtext(0.5, 0.01, 
            f"Wyniki: Luna: {luna_score:.2f} (myszy: {luna_mice}/230, obszar: {area_luna}/{total_area}) | "
            f"Ariana: {ariana_score:.2f} (ślimaki: {ariana_snails}/90, obszar: {area_ariana}/{total_area}) | "
            f"Dante: {dante_score:.2f} (liście+kamienie: {dante_leaves + dante_rocks}/500, obszar: {area_dante}/{total_area})", 
            ha="center", fontsize=12, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

plt.tight_layout()
plt.subplots_adjust(bottom=0.1)
plt.show()

# Dodatkowa analiza równości podziału
print("\nAnaliza równości podziału:")
print(f"Obszar Luny: {area_luna} komórek ({area_luna/total_area*100:.1f}%)")
print(f"Obszar Ariany: {area_ariana} komórek ({area_ariana/total_area*100:.1f}%)")
print(f"Obszar Dantego: {area_dante} komórek ({area_dante/total_area*100:.1f}%)")
print(f"Różnica między największym a najmniejszym regionem: "
      f"{max(area_ariana, area_dante) - min(area_ariana, area_dante)} komórek")

# Sprawdzenie spójności regionów
def check_connectivity(region_mask):
    labeled, num_features = label(region_mask)
    return num_features == 1

print("\nSpójność regionów:")
print(f"Luna: {'spójny' if check_connectivity(labels == 1) else 'NIESPÓJNY!'}")
print(f"Ariana: {'spójny' if check_connectivity(labels == 2) else 'NIESPÓJNY!'}")
print(f"Dante: {'spójny' if check_connectivity(labels == 3) else 'NIESPÓJNY!'}")