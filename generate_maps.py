import json
import os
import random
import re
from tqdm import tqdm
from stqdm import stqdm

from PIL import Image

import DungeonEncounters as DE
from utils.bcolors import bcolors, color_settings

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_dir_720p = "output_720p"
if not os.path.exists(output_dir_720p):
    os.makedirs(output_dir_720p)

grid_size = 100

json_file = "special_tiles.json"
wanderers_file = "wanderers.json"

if not os.path.exists(json_file):
    raise FileNotFoundError(color_settings(f"{json_file} cannot be found.", bcolors.FAIL))
if not os.path.exists(wanderers_file):
    raise FileNotFoundError(color_settings(f"{wanderers_file} cannot be found.", bcolors.FAIL))

with open(json_file, "r") as f:
    special_tiles = json.load(f)

with open(wanderers_file, "r") as f:
    wanderers = json.load(f)

color_to_value = {
    tuple(tile["color"]): int(key, 16) for key, tile in special_tiles.items()
}

value_to_color = {
    int(key, 16): tuple(tile["color"]) for key, tile in special_tiles.items()
}

EMPTY = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "EMPTY"), None)
PATH = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "PATH"), None)
HIDDEN = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "HIDDEN"), None)
CROSS = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "CROSS"), None)
START_FLOOR_0 = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "00"), None)
two_way_positions = {}
one_way_positions = {}

if EMPTY is None or PATH is None or HIDDEN is None or START_FLOOR_0 is None:
    raise ValueError(color_settings("The necessary values are not present in the JSON file.", bcolors.FAIL))


def generate_floor_data(lvl, maps_data=None, maze_type="voronoi", param_1=None, cheat_mode=False):
    max_iterations = 5
    max_map_attempts = 5
    map_attempts = 0

    # Determine ascending coordinates
    if lvl == 0 or len(maps_data) == 0:
        ascending_coords = (50, 50)
    else:
        descending_types = [int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "01"]
        previous_grid = maps_data[-1]["grid"]
        ascending_coords = None
        for DESCENDING in descending_types:
            ascending_coords = next(
                ((x, y) for x in range(grid_size) for y in range(grid_size) if previous_grid[x][y] == DESCENDING),
                None)
            if ascending_coords is not None:
                break

        if ascending_coords is None:
            raise ValueError("No DESCENDING tile found in the previous grid.")

    start_x, start_y = ascending_coords

    while map_attempts < max_map_attempts:
        map_attempts += 1
        iteration = 0

        grid = [[EMPTY for _ in range(grid_size)] for _ in range(grid_size)]  # EMPTY map

        if maze_type == "shuffle":
            maze_type = random.choice(["maze", "road", "voronoi"])
        if maze_type == "maze":
            DE.generate_maze(grid, start_x, start_y, max_depth=param_1 if param_1 is not None else 50)
            print(color_settings(f"Maze (type: maze) generated.", bcolors.OKGREEN))
        elif maze_type == "road":
            DE.generate_road(grid, start_x, start_y, route_width=param_1 if param_1 is not None else 15)
        elif maze_type == "voronoi":
            DE.generate_voronoi(grid, start_x, start_y, num_sites=param_1 if param_1 is not None else 25)
        DE.remove_random_paths(grid, 0.50)

        if cheat_mode is True and lvl == 0:
            DE.cheat_mode(grid, lvl, special_tiles)

        if lvl == 0:
            grid[start_x][start_y] = START_FLOOR_0
            print(color_settings(
                f"'00 Start: z={lvl}, x={start_x}, y={start_y}", bcolors.OKCYAN))
            DE.complete_path(grid, start_x, start_y, "PATH")
        else:
            DE.place_ascending(grid, start_x, start_y, lvl, special_tiles)

        DE.place_wanderers(grid, lvl, wanderers)

        DE.place_descending(grid, start_x, start_y, lvl, special_tiles)

        DE.place_riddles(grid, lvl, special_tiles)

        DE.place_riddles_hints(grid, lvl, special_tiles)

        DE.place_treasure(grid, lvl, special_tiles)

        DE.place_shop(grid, lvl, special_tiles)

        DE.place_teleporter(grid, lvl, two_way_positions, one_way_positions, special_tiles)

        DE.place_ability(grid, lvl, special_tiles)

        DE.place_adventures(grid, lvl, special_tiles)

        DE.place_resurrection(grid, lvl, special_tiles)

        DE.place_healing(grid, lvl, special_tiles)

        DE.place_purification(grid, lvl, special_tiles)

        DE.place_gorgon(grid, lvl, special_tiles)

        DE.place_cavy(grid, lvl, special_tiles)

        DE.place_note(grid, lvl, special_tiles)

        DE.place_movement(grid, lvl, special_tiles)

        DE.place_battle(grid, lvl, special_tiles)

        nb_special_tiles = [
            (x, y) for x in range(grid_size) for y in range(grid_size)
            if grid[x][y] not in [EMPTY, PATH, HIDDEN, CROSS]
        ]

        while iteration < max_iterations:
            if DE.is_connected(grid, start_x, start_y, map_attempts, iteration):
                if 49 < lvl < 59:
                    DE.place_cross(grid, lvl, special_tiles)
                    DE.connect_disconnected_groups(grid)

                if len(nb_special_tiles) == len([(x, y) for x in range(grid_size) for y in range(grid_size) if
                                                 grid[x][y] not in [EMPTY, PATH, HIDDEN, CROSS]]):
                    return grid
                else:
                    print(color_settings("Refinement of the map has broken special tiles. Generating a new map...", bcolors.FAIL))
                    break

            else:
                DE.refine_map(grid)
                iteration += 1

        print(color_settings(
            f"Map attempt {map_attempts} failed after {max_iterations} iterations. Generating a new map...",
            bcolors.WARNING))

    raise RuntimeError(color_settings(f"Unable to generate a connected labyrinth after {max_map_attempts} attempts.",
                                      bcolors.FAIL))


def save_floor_image(grid, output_image_path, output_image_path_720p):
    image = Image.new("RGB", (grid_size, grid_size), value_to_color[EMPTY])
    pixels = image.load()

    for x in range(grid_size):
        for y in range(grid_size):
            pixels[x, y] = value_to_color[grid[x][y]]

    image.save(output_image_path)
    print(color_settings(f"Generated image: {output_image_path}", bcolors.OKGREEN))

    image_720p = Image.new("RGB", (720, 720), value_to_color[EMPTY])
    pixels_720p = image_720p.load()

    scale_factor = 720 // grid_size

    for x in range(grid_size):
        for y in range(grid_size):
            color = value_to_color[grid[x][y]]
            for dx in range(scale_factor):
                for dy in range(scale_factor):
                    pixels_720p[x * scale_factor + dx, y * scale_factor + dy] = color

    image_720p.save(output_image_path_720p)
    print(color_settings(f"Generated 720x720 image: {output_image_path_720p}", bcolors.OKGREEN))


def run(nb_lvl, maze_type="voronoi", param_1=None, generate_bin=False, one_lvl=None, cheat_mode=False):
    if maze_type not in ["maze", "road", "voronoi", "shuffle"]:
        raise ValueError(color_settings('maze_type must be "maze", "road", "voronoi", "shuffle"', bcolors.FAIL))

    maps_data = []

    if one_lvl is not None:
        for lvl in tqdm(one_lvl, desc=color_settings(f"Generating maps...", bcolors.OKGREEN), colour="green"):
            grid = generate_floor_data(lvl=lvl, maps_data=maps_data, maze_type=maze_type, param_1=param_1, cheat_mode=cheat_mode)
            maps_data.append({"level": lvl, "grid": grid})
    else:
        for i in tqdm(range(nb_lvl), desc=color_settings(f"Generating maps...", bcolors.OKGREEN), colour="green"):
            grid = generate_floor_data(lvl=i, maps_data=maps_data, maze_type=maze_type, param_1=param_1, cheat_mode=cheat_mode)
            maps_data.append({"level": i, "grid": grid})

    for data in tqdm(maps_data, desc=color_settings("Saving images and generating binaries", bcolors.WARNING),
                     colour="yellow"):
        lvl = data["level"]
        grid = data["grid"]
        output_image_path = os.path.join(output_dir, f"Map_m{lvl}.png")
        output_image_path_720p = os.path.join(output_dir_720p, f"Map_m{lvl}_720p.png")
        save_floor_image(grid, output_image_path, output_image_path_720p)

        if generate_bin is True:
            DE.reconstruct_bin(lvl=lvl, image_path=output_image_path, output_directory=output_dir)
            print(color_settings(f"Binary and image files for level {lvl} saved in: {output_dir}", bcolors.OKGREEN))


def run_streamlit(nb_lvl, maze_type="voronoi", param_1=None, generate_bin=False, one_lvl=None, cheat_mode=False):
    if maze_type not in ["maze", "road", "voronoi", "shuffle"]:
        raise ValueError(color_settings('maze_type must be "maze", "road", "voronoi", "shuffle"', bcolors.FAIL))

    maps_data = []

    if one_lvl is not None:
        for lvl in stqdm(one_lvl, desc=f"Generating maps..."):
            grid = generate_floor_data(lvl=lvl, maps_data=maps_data, maze_type=maze_type, param_1=param_1, cheat_mode=cheat_mode)
            maps_data.append({"level": lvl, "grid": grid})
    else:
        for i in stqdm(range(nb_lvl), desc=f"Generating maps..."):
            grid = generate_floor_data(lvl=i, maps_data=maps_data, maze_type=maze_type, param_1=param_1, cheat_mode=cheat_mode)
            maps_data.append({"level": i, "grid": grid})

    for data in stqdm(maps_data, desc=color_settings("Saving images and generating binaries", bcolors.WARNING),
                     colour="yellow"):
        lvl = data["level"]
        grid = data["grid"]
        output_image_path = os.path.join(output_dir, f"Map_m{lvl}.png")
        output_image_path_720p = os.path.join(output_dir_720p, f"Map_m{lvl}_720p.png")
        save_floor_image(grid, output_image_path, output_image_path_720p)

        if generate_bin:
            DE.reconstruct_bin(lvl=lvl, image_path=output_image_path, output_directory=output_dir)
            print(color_settings(f"Binary and image files for level {lvl} saved in: {output_dir}", bcolors.OKGREEN))


if __name__ == "__main__":
    run(nb_lvl=100, maze_type="shuffle", generate_bin=False, one_lvl=None, cheat_mode=False)
