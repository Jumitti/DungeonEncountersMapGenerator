import json
import os
import random
import re

from PIL import Image

import DungeonEncounters as DE

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

grid_size = 100

json_file = "special_tiles.json"
wanderers_file = "wanderers.json"

if not os.path.exists(json_file):
    raise FileNotFoundError(f"{json_file} cannot be found.")
if not os.path.exists(wanderers_file):
    raise FileNotFoundError(f"{wanderers_file} cannot be found.")

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

EMPTY = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "EMPTY"), None)
CASE = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "CASE"), None)
HIDDEN = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "HIDDEN"), None)
START_FLOOR_0 = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "00"), None)
DESCENDING = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "01"), None)
ASCENDING = next((int(key, 16) for key, case in special_cases.items() if case["name"] == "02"), None)
two_way_positions = {}

if EMPTY is None or CASE is None or HIDDEN is None or START_FLOOR_0 is None or DESCENDING is None or ASCENDING is None:
    raise ValueError("The necessary values are not present in the JSON file.")


def generate_floor(lvl, ascending_coords=None):
    output_image_path = os.path.join(output_dir, f"Map_m{lvl}.png")

    grid = [[EMPTY for _ in range(grid_size)] for _ in range(grid_size)]  # EMPTY map

    # Map initiation coordinates
    if lvl == 0:
        ascending_coords = (50, 50)
    start_x, start_y = ascending_coords

    DE.generate_voronoi(grid, start_x, start_y)

    DE.remove_random_paths(grid, 0.50)

    if lvl == 0:
        grid[start_x][start_y] = START_FLOOR_0
    elif lvl > 0 and ascending_coords:
        grid[start_x][start_y] = ASCENDING
    DE.complete_path(grid, start_x, start_y, "CASE")

    case_positions = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] in {CASE, HIDDEN}]

    descending_coords = None
    farthest_positions = sorted(
        [(cx, cy) for cx, cy in case_positions],
        key=lambda pos: (pos[0] - start_x) ** 2 + (pos[1] - start_y) ** 2,
        reverse=True
    )

    for cx, cy in farthest_positions:
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY:
                    grid[nx][ny] = DESCENDING
                    DE.complete_path(grid, nx, ny, "RANDOM")
                    descending_coords = (nx, ny)
                    break
            if descending_coords:
                break
        if descending_coords:
            break

    for wanderer_name, wanderer_data in wanderers.items():
        coords = wanderer_data["coord"]
        for coord in coords:
            wy, wx = coord[1], coord[2]

            if lvl == coord[0]:
                DE.complete_path(grid, wx, wy, "HIDDEN")
                grid[wx][wy] = CASE
                print(f"Wanderer {wanderer_data['name']} placed ({wy}, {wx})")

    for riddle in ["Map Riddle", "Math Riddle"]:
        for riddle_name, riddle_data in special_cases.items():
            if "other_name" in riddle_data:
                name, other_name = riddle_data["name"], riddle_data["other_name"]
                if isinstance(other_name, list):
                    other_name = " ".join(other_name)
                if re.search(riddle, other_name):
                    coords = riddle_data["coord"]
                    for coord in coords:
                        wy, wx = coord[1], coord[2]

                        if lvl == coord[0]:
                            DE.complete_path(grid, wx, wy, "RANDOM")
                            grid[wx][wy] = next(
                                (int(key, 16) for key, case in special_cases.items() if case["name"] == name), None)
                            print(f"{riddle} '{riddle_data['name']}' placed ({lvl}, {wx}, {wy})")

    for k in range(1, 11):
        for two_way_name, two_way_data in special_cases.items():
            if "other_name" in two_way_data:
                name, other_name = two_way_data["name"], two_way_data["other_name"]
                if isinstance(other_name, list):
                    other_name = " ".join(other_name)
                if re.search(f"Two-way Teleporter {k}", other_name):
                    coords = two_way_data["coord"]

                    if name in two_way_positions and len(two_way_positions[name]) >= 2:
                        continue

                    for coord in coords:
                        if lvl == coord[0]:
                            random.shuffle(case_positions)

                            for cx, cy in case_positions:
                                dx, dy = random.randint(-4, 4), random.randint(-4, 4)
                                nx, ny = cx + dx, cy + dy
                                if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY:
                                    grid[nx][ny] = next(
                                        (int(key, 16) for key, case in special_cases.items() if case["name"] == name),
                                        None)
                                    DE.complete_path(grid, nx, ny, "RANDOM")

                                    if name not in two_way_positions:
                                        two_way_positions[name] = []
                                    two_way_positions[name].append((lvl, nx, ny))
                                    print(f"Two-way Teleporter {k} '{two_way_data['name']}' placed ({lvl}, {nx}, {ny})")

                                    break

    max_iterations = 100
    iteration = 0
    need_refine_map = True

    while need_refine_map and iteration < max_iterations:
        if DE.is_connected(grid, start_x, start_y):
            print("The labyrinth is connected.")
            need_refine_map = False
        else:
            print(f"The labyrinth is not connected. Refinement in progress... (Iteration {iteration + 1})")
            DE.refine_map(grid)
            iteration += 1

    if iteration >= max_iterations:
        print("Error: Unable to fully connect the card after several attempts.")

    image = Image.new("RGB", (grid_size, grid_size), value_to_color[EMPTY])
    pixels = image.load()

    for x in range(grid_size):
        for y in range(grid_size):
            pixels[x, y] = value_to_color[grid[x][y]]

    image.save(output_image_path)
    print(f"Generated image :{output_image_path}")

    return descending_coords, output_image_path


def run(nb_lvl, maze_type="voronoi", generate_bin=False):
    descending_coords = None

    if maze_type not in ["maze", "road", "voronoi", "shuffle"]:
        raise ValueError('maze_type must be "maze", "road", "voronoi", "shuffle"')

    for i in range(nb_lvl):

        descending_coords, image_path = generate_floor(lvl=i, ascending_coords=descending_coords)

        if generate_bin:
            DE.reconstruct_bin(lvl=i, image_path=image_path, output_directory=output_dir)
            print(f"Image and binary file for maze {i} generated in 'output' folder.")


if __name__ == "__main__":
    run(nb_lvl=3, maze_type="shuffle", generate_bin=True)
