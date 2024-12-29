import json
import random
import numpy as np
from collections import deque
from random import shuffle, choice
from scipy.spatial import Voronoi, voronoi_plot_2d

from PIL import Image


def reconstruct_bin(image_path, json_path, output_bin_path):
    # Charger l'image
    image = Image.open(image_path)
    pixels = image.load()

    # Charger le fichier JSON
    with open(json_path, "r") as f:
        special_cases = json.load(f)

    # Vérifier si l'image est bien de 100x100
    width, height = image.size
    if width != 100 or height != 100:
        raise ValueError("L'image doit être de taille 100x100 pixels.")

    # Ouvrir le fichier bin en mode écriture
    with open(output_bin_path, "wb") as f:
        for y in range(100):
            for x in range(100):
                # Récupérer la couleur du pixel
                r, g, b = pixels[x, y]

                # Trouver la valeur hexadécimale correspondant à cette couleur dans le JSON
                hex_value = None
                for key, case in special_cases.items():
                    # Comparer la couleur de la case avec la couleur du pixel
                    if case["color"] == [r, g, b]:
                        hex_value = int(key, 16)
                        break

                if hex_value is None:
                    raise ValueError(f"Aucune valeur trouvée pour la couleur {r, g, b} à la position ({x}, {y})")

                # Convertir l'entier en 3 octets et l'écrire dans le fichier bin
                f.write(hex_value.to_bytes(3, 'big'))

    print(f"Le fichier {output_bin_path} a été généré avec succès.")


# Fonction pour vérifier si les cases adjacentes à gauche et à droite sont vides
def is_valid_move(grid, x, y, dx, dy, EMPTY=next(
    (int(key, 16) for key, case in json.load(open("special_case.json")).items() if case["name"] == "EMPTY"), None),
                  grid_size=100):
    for i in range(5, 20):  # Vérifie si au moins 3 cases sur le côté sont vides
        nx, ny = x + dx * i, y + dy * i
        if not (0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY):
            return False
    return True


# Fonction pour générer un labyrinthe à partir du point de départ (50, 50)
def generate_maze(grid, x, y, max_depth=50, CASE=next(
    (int(key, 16) for key, case in json.load(open("special_case.json")).items() if case["name"] == "CASE"), None),
                  grid_size=100):
    if max_depth <= 0:
        return

    # Directions possibles : haut, bas, gauche, droite
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)  # Mélanger les directions

    for dx, dy in directions:
        # Vérifie si le mouvement est valide : il doit y avoir 3 cases vides à côté
        if is_valid_move(grid, x, y, dx, dy):
            # Faire avancer dans la direction choisie
            for i in range(1, 5):
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    grid[nx][ny] = CASE  # Marquer la case comme un chemin
            # Appel récursif pour continuer à générer dans cette direction
            generate_maze(grid, nx, ny, max_depth - 1)


def generate_random_routes(grid, grid_size=100, x=50, y=50, route_width=3,
                           CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                      case["name"] == "CASE"), None),
                           EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                       case["name"] == "EMPTY"), None)):
    # Liste des positions à explorer
    def neighbors(x, y):
        return [(x + dx, y + dy) for dx, dy in
                [(0, route_width), (route_width, 0), (0, -route_width), (-route_width, 0)]
                if 0 <= x + dx < grid_size and 0 <= y + dy < grid_size]

    grid[x][y] = CASE
    frontier = neighbors(x, y)
    shuffle(frontier)

    while frontier:
        nx, ny = frontier.pop()
        if grid[nx][ny] == EMPTY:
            # Marquer les cases comme route
            for i in range(route_width):
                if 0 <= nx - i < grid_size:
                    grid[nx - i][ny] = CASE
                if 0 <= ny - i < grid_size:
                    grid[nx][ny - i] = CASE

            # Ajouter les voisins
            for neighbor in neighbors(nx, ny):
                if grid[neighbor[0]][neighbor[1]] == EMPTY:
                    frontier.append(neighbor)
            shuffle(frontier)

    return grid


def generate_voronoi_map(grid, start_x, start_y, grid_size=20, num_sites=20,
                         CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                    case["name"] == "CASE"), None),
                         EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                     case["name"] == "EMPTY"), None)
                         ):

    # Positionner les sites, en plaçant le premier site au centre spécifié
    sites = np.array([[start_x, start_y]] + [[random.randint(start_x - grid_size, start_x + grid_size),
                                     random.randint(start_y - grid_size, start_y + grid_size)] for _ in
                                    range(num_sites - 1)])

    vor = Voronoi(sites)

    # Tracer les arêtes sur la grille
    for ridge in vor.ridge_vertices:
        if -1 in ridge:  # Ignorer les arêtes infinies
            continue
        start, end = vor.vertices[ridge]
        start = np.round(start).astype(int)
        end = np.round(end).astype(int)

        # Vérifier si les points sont dans les limites de la grille
        if 0 <= start[0] < start_x + grid_size and 0 <= start[1] < start_y + grid_size and \
                0 <= end[0] < start_x + grid_size and 0 <= end[1] < start_y + grid_size:
            # Tracer une ligne entre start et end
            for x, y in bresenham_line(start[0], start[1], end[0], end[1]):
                if 0 <= x < start_x + grid_size and 0 <= y < start_y + grid_size:
                    grid[x][y] = CASE

    return grid

def bresenham_line(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return points


# Fonction pour effectuer une recherche en profondeur pour vérifier la connectivité
def dfs(grid, x, y, visited,
        CASE=next(
            (int(key, 16) for key, case in json.load(open("special_case.json")).items() if case["name"] == "CASE"),
            None), grid_size=100):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) not in visited:
            visited.add((cx, cy))
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == CASE:
                    stack.append((nx, ny))


def is_connected(grid, start_x, start_y, CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                   case["name"] == "CASE"), None),
                        EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                    case["name"] == "EMPTY"), None),
                 grid_size=100):
    # Vérifier si la grille est connectée en utilisant DFS (Depth-First Search)
    visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]  # Matrice de visites
    stack = [(start_x, start_y)]  # Pile pour DFS

    # Directions possibles (haut, bas, gauche, droite)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    visited[start_x][start_y] = True  # Marquer le point de départ comme visité
    visited_count = 1  # Compter le nombre de CASE visitées

    # Parcours DFS
    while stack:
        x, y = stack.pop()

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Vérifier les limites de la grille et si la case est un chemin (CASE)
            if 0 <= nx < grid_size and 0 <= ny < grid_size and not visited[nx][ny] and grid[nx][ny] == CASE:
                visited[nx][ny] = True
                stack.append((nx, ny))
                visited_count += 1

    # Vérifier si toutes les cases marquées CASE ont été visitées
    total_case_count = sum(row.count(CASE) for row in grid)
    return visited_count == total_case_count

def remove_random_paths(grid, percentage_to_remove,
                        CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                   case["name"] == "CASE"), None),
                        EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                    case["name"] == "EMPTY"), None), grid_size=100):
    # Liste de toutes les cases appartenant au chemin
    paths = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] == CASE]
    random.shuffle(paths)

    # Nombre total de cases à supprimer
    num_to_remove = int(len(paths) * percentage_to_remove)
    start_x, start_y = next((x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] == CASE)

    for i in range(num_to_remove):
        x, y = paths[i]
        to_remove = [(x, y)]  # Commencer avec la case actuelle
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Directions adjacentes

        # Ajouter 1 ou 2 cases adjacentes si elles appartiennent aussi au chemin
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == CASE:
                to_remove.append((nx, ny))
                if len(to_remove) == 5:  # Limiter à 3 cases au maximum
                    break

        # Supprimer les cases sélectionnées
        removed_cases = []
        for rx, ry in to_remove:
            grid[rx][ry] = EMPTY
            removed_cases.append((rx, ry))

        # Vérifier la connectivité après suppression
        visited = set()
        dfs(grid, start_x, start_y, visited)

        # Si le réseau n'est plus connecté, restaurer les cases supprimées
        if len(visited) != sum(1 for px, py in paths if grid[px][py] == CASE):
            for rx, ry in removed_cases:
                grid[rx][ry] = CASE


def complete_path_with_hidden(grid, x, y, case_type="RANDOM",
                              CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items()
                                         if case["name"] == "CASE"), None),
                              EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                          case["name"] == "EMPTY"), None),
                              HIDDEN=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                           case["name"] == "HIDDEN"), None), grid_size=100):
    # Effectuer un BFS ou DFS pour trouver le chemin en diagonale vers la case CASE et le remplir avec HIDDEN
    visited = set()
    queue = deque([(x, y, [])])  # On garde la trajectoire parcourue
    visited.add((x, y))

    # Choisir la case cible en fonction de case_type
    if case_type == "RANDOM":
        # Choisir aléatoirement entre CASE et HIDDEN
        target_case = random.choice([CASE, HIDDEN])
    elif case_type == "CASE":
        target_case = CASE
    elif case_type == "HIDDEN":
        target_case = HIDDEN
    else:
        raise ValueError(f"case_type invalide: {case_type}")

    while queue:
        cx, cy, path = queue.popleft()

        if grid[cx][cy] == CASE:
            # Si on a atteint la case cible, remplir le chemin avec la case target_case
            for px, py in path:
                if grid[px][py] == EMPTY:
                    grid[px][py] = target_case
            return path

        # Ajouter les cases adjacentes (y compris diagonales)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0),
                       (1, -1), (-1, 1), (1, 1), (-1, -1)]:  # diagonales
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] in [EMPTY, CASE] and (
                    nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))
