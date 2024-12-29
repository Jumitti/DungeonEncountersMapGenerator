import json
from PIL import Image
import random
import os
from collections import deque
import DungeonEncounters as DE
import re

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

grid_size = 100

json_file = "special_case.json"
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

if EMPTY is None or CASE is None or HIDDEN is None or START_FLOOR_0 is None or DESCENDING is None or ASCENDING is None:
    raise ValueError("The necessary values are not present in the JSON file.")


def generate_floor_image(output_image_path, i, ascending_coords=None):
    grid = [[EMPTY for _ in range(grid_size)] for _ in range(grid_size)]

    if i == 0:
        start_x, start_y = 50, 50
    elif i > 0 and ascending_coords:
        ax, ay = ascending_coords
        start_x, start_y = ax, ay

    grid[start_x][start_y] = CASE

    DE.generate_voronoi_map(grid, start_x, start_y)

    DE.remove_random_paths(grid, 0.50)

    if i == 0:
        grid[50][50] = START_FLOOR_0
    elif i > 0 and ascending_coords:
        grid[ax][ay] = ASCENDING

    case_positions = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] in {CASE, HIDDEN}]
    random.shuffle(case_positions)

    descending_coords = None
    for cx, cy in case_positions:
        dx, dy = random.randint(-4, 4), random.randint(-4, 4)
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY:
            grid[nx][ny] = DESCENDING
            DE.complete_path_with_hidden(grid, nx, ny, "RANDOM")
            descending_coords = (nx, ny)
            break

    for wanderer_name, wanderer_data in wanderers.items():
        coords = wanderer_data["coord"]
        for coord in coords:
            wy, wx = coord[1], coord[2]

            if i == coord[0]:
                DE.complete_path_with_hidden(grid, wx, wy, "HIDDEN")
                grid[wx][wy] = CASE
                print(f"Wanderer {wanderer_data['name']} placé à ({wy}, {wx})")

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

                        if i == coord[0]:
                            DE.complete_path_with_hidden(grid, wx, wy, "RANDOM")
                            grid[wx][wy] = next(
                                (int(key, 16) for key, case in special_cases.items() if case["name"] == name), None)
                            print(f"{riddle} '{riddle_data['name']}' placé à ({i}, {wx}, {wy})")

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

    return descending_coords


def run(nb_maps, generate_bin=False):
    for j in range(nb_maps):
        image_path = os.path.join(output_dir, f"generated_maze_{j}.png")
        json_path = "special_case.json"
        output_bin_path = os.path.join(output_dir, f"Map_m{j}.bin")

        if j == 0:
            descending_coords = generate_floor_image(image_path, j)
        else:
            descending_coords = generate_floor_image(image_path, j, ascending_coords=descending_coords)

        if generate_bin is True:
            DE.reconstruct_bin(image_path, json_path, output_bin_path)

            print(f"Image and binary file for maze {j} generated in 'output' folder.")


if __name__ == "__main__":
    run(nb_maps=5, generate_bin=False)
