import json
from PIL import Image
import random
import os
from collections import deque
import DungeonEncounters as DE

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

grid_size = 100  # Taille de la grille

json_file = "special_case.json"
if not os.path.exists(json_file):
    raise FileNotFoundError(f"{json_file} est introuvable.")

with open(json_file, "r") as f:
    special_cases = json.load(f)

color_to_value = {
    tuple(case["color"]): int(key, 16) for key, case in special_cases.items()
}

value_to_color = {
    int(key, 16): tuple(case["color"]) for key, case in special_cases.items()
}

# Récupérer dynamiquement les valeurs hexadécimales basées sur le "name"
EMPTY = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "EMPTY"), None)
CASE = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "CASE"), None)
START_FLOOR_0 = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "00"), None)
DESCENDING = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "01"), None)
ASCENDING = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "02"), None)

# Trouver la case correspondant à "83"
case_83 = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "83"), None)
if case_83 is None:
    raise ValueError("La case '83' n'a pas été trouvée dans le fichier JSON.")

# Vérification si les autres valeurs nécessaires sont présentes
if EMPTY is None or CASE is None or START_FLOOR_0 is None or DESCENDING is None or ASCENDING is None:
    raise ValueError("Les valeurs nécessaires ne sont pas présentes dans le fichier JSON.")

# Fonction pour générer l'image du labyrinthe
def generate_floor_image(output_image_path, i, ascending_coords=None):
    grid = [[EMPTY for _ in range(grid_size)] for _ in range(grid_size)]

    # Si i == 0, place START_FLOOR_0 à (50, 50) et commence à partir de là
    if i == 0:
        start_x, start_y = 50, 50  # Point de départ du labyrinthe (50, 50)
    elif i > 0 and ascending_coords:
        ax, ay = ascending_coords
        start_x, start_y = ax, ay  # Point de départ du labyrinthe basé sur ASCENDING

    grid[start_x][start_y] = CASE  # Marquer le point de départ comme un chemin

    DE.generate_maze(grid, start_x, start_y,
                  max_depth=20)  # Générer le labyrinthe avec une profondeur plus élevée pour mieux connecter

    DE.remove_random_paths(grid, 0.5)  # Suppression de 50% des chemins

    if i == 0:
        grid[50][50] = START_FLOOR_0
    elif i > 0 and ascending_coords:
        grid[ax][ay] = ASCENDING

    case_positions = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] == CASE]
    random.shuffle(case_positions)

    descending_coords = None
    for cx, cy in case_positions:
        # Placer DESCENDING à une distance aléatoire de 0 à 3 autour de CASE
        dx, dy = random.randint(-4, 4), random.randint(-4, 4)
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY:
            grid[nx][ny] = DESCENDING
            DE.complete_path_with_hidden(grid, nx, ny, "RANDOM")  # Compléter avec HIDDEN autour de DESCENDING
            descending_coords = (nx, ny)
            break

    # Créer l'image en utilisant les couleurs définies dans le JSON
    image = Image.new("RGB", (grid_size, grid_size), value_to_color[EMPTY])
    pixels = image.load()

    for x in range(grid_size):
        for y in range(grid_size):
            pixels[x, y] = value_to_color[grid[x][y]]

    image.save(output_image_path)
    print(f"Image générée : {output_image_path}")

    return descending_coords


for j in range(100):
    # Définir les chemins d'enregistrement des fichiers dans le dossier output
    image_path = os.path.join(output_dir, f"generated_maze_{j}.png")
    json_path = "special_case.json"  # Fichier JSON
    output_bin_path = os.path.join(output_dir, f"Map_m{j}.bin")  # Fichier binaire de sortie

    # Générer l'image du labyrinthe avant de reconstruire le fichier binaire
    if j == 0:
        descending_coords = generate_floor_image(image_path, j)
    else:
        descending_coords = generate_floor_image(image_path, j, ascending_coords=descending_coords)

    # Une fois l'image générée, reconstruire le fichier binaire
    DE.reconstruct_bin(image_path, json_path, output_bin_path)

    print(f"Image et fichier binaire pour le labyrinthe {j} générés dans le dossier 'output'.")
