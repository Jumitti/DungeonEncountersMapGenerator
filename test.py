import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import random

def generate_voronoi_map(grid_size=100, num_sites=10,
                         CASE=1,  # Valeur représentant les arêtes
                         EMPTY=0  # Valeur représentant le vide
                         ):
    """
    Génère un diagramme de Voronoi sur une grille. Les arêtes sont marquées comme CASE et les autres cases comme EMPTY.

    :param grid_size: Taille de la grille (grid_size x grid_size).
    :param num_sites: Nombre de points générateurs pour le diagramme de Voronoi.
    :param CASE: Valeur attribuée aux arêtes du diagramme.
    :param EMPTY: Valeur attribuée aux autres cases de la grille.
    :return: Une grille 2D numpy contenant le diagramme de Voronoi.
    """
    # Génération de points générateurs (sites)
    sites = np.array([[random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)] for _ in range(num_sites)])

    # Création du diagramme de Voronoi
    vor = Voronoi(sites)

    # Initialisation de la grille
    grid = np.full((grid_size, grid_size), EMPTY)

    # Parcourir les arêtes du diagramme de Voronoi
    for ridge in vor.ridge_vertices:
        if -1 in ridge:  # Ignorer les arêtes infinies
            continue
        start, end = vor.vertices[ridge]
        start = np.round(start).astype(int)
        end = np.round(end).astype(int)

        # Vérifier si les points sont dans les limites de la grille
        if 0 <= start[0] < grid_size and 0 <= start[1] < grid_size and \
           0 <= end[0] < grid_size and 0 <= end[1] < grid_size:
            # Tracer les lignes entre start et end
            for x, y in bresenham_line(start[0], start[1], end[0], end[1]):
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    grid[x, y] = CASE

    return grid


def bresenham_line(x1, y1, x2, y2):
    """
    Implémente l'algorithme de tracé de ligne de Bresenham pour générer une ligne discrète.

    :param x1, y1: Coordonnées de départ.
    :param x2, y2: Coordonnées d'arrivée.
    :return: Une liste de coordonnées (x, y) représentant la ligne discrète.
    """
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


def visualize_voronoi(grid):
    """
    Visualise la grille avec matplotlib.

    :param grid: Une grille 2D numpy contenant les valeurs CASE et EMPTY.
    """
    plt.figure(figsize=(10, 10))
    plt.imshow(grid.T, cmap='Greys', origin='lower', interpolation='nearest')
    plt.title("Voronoi Diagram")
    plt.show()


# Exemple d'utilisation
grid_size = 100
num_sites = 10

# Générer une carte de Voronoi
grid = generate_voronoi_map(grid_size=grid_size, num_sites=num_sites)

# Visualiser la carte
visualize_voronoi(grid)
