objects = [
    ('mysz polna', 45, [0.4, 0.125, 0.2]),
    ('mysz domowa', 28, [0.4, 0.125, 0.2]),
    ('slimak', 27, [0.1, 0.375, 0.05]),
    ('lisc', 6, [0.0, 0.375, 0.05]),
    ('kamyk', 4, [0.1, 0.0, 0.5])
]
cat_names = ['Luna', 'Ariana', 'Dante']
capacity = 2000

# Dla każdego kota
for cat_index in range(3):
    items = []
    original_values = []
    volumes = []
    
    for obj in objects:
        vol = obj[1]
        orig_val = obj[2][cat_index]
        new_val = 1 + orig_val
        items.append((vol, new_val))
        original_values.append(orig_val)
        volumes.append(vol)
    
    n_items = len(items)
    
    dp = [-10**9] * (capacity + 1)
    dp[0] = 0
    parent = [-1] * (capacity + 1)
    
    for j in range(1, capacity + 1):
        for i in range(n_items):
            vol, new_val = items[i]
            if j >= vol:
                if dp[j] < dp[j - vol] + new_val:
                    dp[j] = dp[j - vol] + new_val
                    parent[j] = i
    
    max_val = -10**9
    j_max = 0
    for j in range(capacity + 1):
        if dp[j] > max_val:
            max_val = dp[j]
            j_max = j
    
    counts = [0] * n_items
    j = j_max
    while j > 0:
        i = parent[j]
        if i == -1:
            break
        counts[i] += 1
        j -= volumes[i]
    
    total_objects = sum(counts)
    total_original_value = sum(counts[i] * original_values[i] for i in range(n_items))
    score = 0.5 * total_objects + 0.5 * total_original_value
    

    print(f"Cat: {cat_names[cat_index]}")
    print(f"  Objects: field_mouse={counts[0]}, house_mouse={counts[1]}, snail={counts[2]}, leaf={counts[3]}, rock={counts[4]}")
    print(f"  Total objects: {total_objects}")
    print(f"  Total value: {total_original_value:.2f}")
    print(f"  Score: {score:.2f}\n")