import json
from PIL import Image
import random
import os
from collections import deque
import DungeonEncounters as DE
import re  # Assurez-vous que re est importé

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

grid_size = 100  # Taille de la grille

json_file = "special_case.json"
wanderers_file = "wanderers.json"  # Nouveau fichier contenant les Wanderers

# Charger les fichiers JSON
if not os.path.exists(json_file):
    raise FileNotFoundError(f"{json_file} est introuvable.")
if not os.path.exists(wanderers_file):
    raise FileNotFoundError(f"{wanderers_file} est introuvable.")

with open(json_file, "r") as f:
    special_cases = json.load(f)

with open(wanderers_file, "r") as f:
    wanderers = json.load(f)

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

    DE.generate_voronoi_map(grid, start_x, start_y)  # Générer le labyrinthe avec une profondeur plus élevée pour mieux connecter

    DE.remove_random_paths(grid, 0.50)  # Suppression de 50% des chemins

    # Vérification de la connectivité des CASE
    if DE.is_connected(grid, start_x, start_y):
        print("Le labyrinthe est connecté.")
    else:
        print("Le labyrinthe n'est pas connecté.")

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

        # Ajouter les Wanderers à la grille
    for wanderer_name, wanderer_data in wanderers.items():
        coords = wanderer_data["coord"]
        for coord in coords:
            wy, wx = coord[1], coord[2]  # Utilisation des coordonnées x et y (coord[2], coord[1])

            # Vérifier si le Wanderer doit être placé sur cet étage
            if i == coord[0]:
                DE.complete_path_with_hidden(grid, wx, wy, "HIDDEN")  # Compléter avec HIDDEN autour du Wanderer
                grid[wx][wy] = CASE  # Place un CASE (ou une autre valeur spécifique) pour le Wanderer
                print(f"Wanderer {wanderer_data['name']} placé à ({wy}, {wx})")

    for map_name, map_date in special_cases.items():
        # Vérification si 'other_name' existe et est bien une chaîne
        if "other_name" in map_date:
            # Si 'other_name' est une liste, on la transforme en une chaîne
            name, other_name = map_date["name"], map_date["other_name"]
            if isinstance(other_name, list):
                other_name = " ".join(other_name)  # Concatène les éléments de la liste en une seule chaîne
            if re.search("Map Riddle", other_name):
                coords = map_date["coord"]
                for coord in coords:
                    wy, wx = coord[1], coord[2]

                    if i == coord[0]:
                        DE.complete_path_with_hidden(grid, wx, wy, "RANDOM")
                        grid[wx][wy] = next((int(key, 16) for key, case in special_cases.items() if case["name"] == name), None)
                        print(f"Map Riddle '{map_date['name']}' placé à ({i}, {wx}, {wy})")

    for math_name, math_date in special_cases.items():
        # Vérification si 'other_name' existe et est bien une chaîne
        if "other_name" in math_date:
            # Si 'other_name' est une liste, on la transforme en une chaîne
            name, other_name = math_date["name"], math_date["other_name"]
            if isinstance(other_name, list):
                other_name = " ".join(other_name)  # Concatène les éléments de la liste en une seule chaîne
            if re.search("Math Riddle", other_name):
                coords = math_date["coord"]
                for coord in coords:
                    wy, wx = coord[1], coord[2]

                    if i == coord[0]:
                        DE.complete_path_with_hidden(grid, wx, wy, "RANDOM")
                        grid[wx][wy] = next((int(key, 16) for key, case in special_cases.items() if case["name"] == name), None)
                        print(f"Math Riddle '{math_date['name']}' placé à ({i}, {wx}, {wy})")

    # # Vérifier les cases non-EMPTY entourées de EMPTY et les remplir
    for x in range(1, grid_size - 1):  # On commence à 1 et on s'arrête à grid_size - 1 pour ne pas sortir des limites
        for y in range(1, grid_size - 1):
            if grid[x][y] != EMPTY:  # Vérifier les cases non-EMPTY
                # Cas 1: Vérifier si la case est entourée de cases vides (horizontale, verticale, et diagonales)
                if (grid[x - 1][y] == EMPTY and grid[x + 1][y] == EMPTY and
                        grid[x][y - 1] == EMPTY and grid[x][y + 1] == EMPTY and
                        grid[x - 1][y - 1] == EMPTY and grid[x - 1][y + 1] == EMPTY and
                        grid[x + 1][y - 1] == EMPTY and grid[x + 1][y + 1] == EMPTY):

                    value_case = grid[x][y]
                    grid[x][y] = EMPTY
                    DE.complete_path_with_hidden(grid, x, y, "RANDOM")  # Compléter avec HIDDEN autour de la case
                    grid[x][y] = value_case
                    print(
                        f"Case isolée à ({x}, {y}) entourée de cases vides (y compris les diagonales), remplie avec CASE.")

                # Cas 2: Vérifier si la case est entourée horizontalement et verticalement par des cases vides,
                # mais au moins une diagonale est non vide, ajouter une CASE entre la diagonale et la case
                elif (grid[x - 1][y] == EMPTY and grid[x + 1][y] == EMPTY and
                      grid[x][y - 1] == EMPTY and grid[x][y + 1] == EMPTY):

                    # Vérifier les diagonales valides
                    if grid[x - 1][y - 1] != EMPTY:  # Diagonale haut-gauche
                        grid[x - 1][y] = CASE  # Ajouter une CASE entre haut-gauche et case
                        print(f"Ajout d'une CASE entre la diagonale haut-gauche et la case ({x}, {y})")
                    elif grid[x - 1][y + 1] != EMPTY:  # Diagonale haut-droite
                        grid[x - 1][y] = CASE  # Ajouter une CASE entre haut-droite et case
                        print(f"Ajout d'une CASE entre la diagonale haut-droite et la case ({x}, {y})")
                    elif grid[x + 1][y - 1] != EMPTY:  # Diagonale bas-gauche
                        grid[x + 1][y] = CASE  # Ajouter une CASE entre bas-gauche et case
                        print(f"Ajout d'une CASE entre la diagonale bas-gauche et la case ({x}, {y})")
                    elif grid[x + 1][y + 1] != EMPTY:  # Diagonale bas-droite
                        grid[x + 1][y] = CASE  # Ajouter une CASE entre bas-droite et case
                        print(f"Ajout d'une CASE entre la diagonale bas-droite et la case ({x}, {y})")

    # Créer l'image en utilisant les couleurs définies dans le JSON
    image = Image.new("RGB", (grid_size, grid_size), value_to_color[EMPTY])
    pixels = image.load()

    for x in range(grid_size):
        for y in range(grid_size):
            pixels[x, y] = value_to_color[grid[x][y]]

    image.save(output_image_path)
    print(f"Image générée : {output_image_path}")

    return descending_coords


def run(nb_maps, generate_bin=False):
    for j in range(nb_maps):
        # Définir les chemins d'enregistrement des fichiers dans le dossier output
        image_path = os.path.join(output_dir, f"generated_maze_{j}.png")
        json_path = "special_case.json"  # Fichier JSON
        output_bin_path = os.path.join(output_dir, f"Map_m{j}.bin")  # Fichier binaire de sortie

        # Générer l'image du labyrinthe avant de reconstruire le fichier binaire
        if j == 0:
            descending_coords = generate_floor_image(image_path, j)
        else:
            descending_coords = generate_floor_image(image_path, j, ascending_coords=descending_coords)

        if generate_bin is True:
            # Une fois l'image générée, reconstruire le fichier binaire
            DE.reconstruct_bin(image_path, json_path, output_bin_path)

            print(f"Image et fichier binaire pour le labyrinthe {j} générés dans le dossier 'output'.")


if __name__ == "__main__":
    run(4, generate_bin=False)
