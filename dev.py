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
START_FLOOR_0 = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "00"), None)
DESCENDING = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "01"), None)
ASCENDING = next((int(key, 16) for key, tile in special_tiles.items() if tile["name"] == "02"), None)
two_way_positions = {}

if EMPTY is None or PATH is None or HIDDEN is None or START_FLOOR_0 is None or DESCENDING is None or ASCENDING is None:
    raise ValueError("The necessary values are not present in the JSON file.")


def generate_floor_data(lvl, maps_data=None):
    max_iterations = 5
    max_map_attempts = 5
    map_attempts = 0

    # Determine ascending coordinates
    if lvl == 0:
        ascending_coords = (50, 50)
    else:
        previous_grid = maps_data[-1]["grid"]
        ascending_coords = next(
            (x, y) for x in range(grid_size) for y in range(grid_size) if previous_grid[x][y] == DESCENDING
        )
    start_x, start_y = ascending_coords

    while map_attempts < max_map_attempts:
        map_attempts += 1
        iteration = 0

        grid = [[EMPTY for _ in range(grid_size)] for _ in range(grid_size)]  # EMPTY map

        DE.generate_voronoi(grid, start_x, start_y)
        DE.remove_random_paths(grid, 0.50)

        grid[start_x][start_y] = START_FLOOR_0 if lvl == 0 else ASCENDING
        DE.complete_path(grid, start_x, start_y, "PATH")

        tile_positions = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] in {PATH, HIDDEN}]
        descending_coords = None
        farthest_positions = sorted(
            [(cx, cy) for cx, cy in tile_positions],
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
                    grid[wx][wy] = PATH
                    print(f"Wanderer {wanderer_data['name']} placed ({wy}, {wx})")

        for riddle in ["Map Riddle", "Math Riddle"]:
            for riddle_name, riddle_data in special_tiles.items():
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
                                    (int(key, 16) for key, tile in special_tiles.items() if tile["name"] == name), None)
                                print(f"{riddle} '{riddle_data['name']}' placed ({lvl}, {wx}, {wy})")

        for k in range(1, 11):
            for two_way_name, two_way_data in special_tiles.items():
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
                                random.shuffle(tile_positions)

                                for cx, cy in tile_positions:
                                    dx, dy = random.randint(-4, 4), random.randint(-4, 4)
                                    nx, ny = cx + dx, cy + dy
                                    if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY:
                                        grid[nx][ny] = next(
                                            (int(key, 16) for key, tile in special_tiles.items() if
                                             tile["name"] == name),
                                            None)
                                        DE.complete_path(grid, nx, ny, "RANDOM")

                                        if name not in two_way_positions:
                                            two_way_positions[name] = []
                                        two_way_positions[name].append((lvl, nx, ny))
                                        print(
                                            f"Two-way Teleporter {k} '{two_way_data['name']}' placed ({lvl}, {nx}, {ny})")

                                        break

        while iteration < max_iterations:
            if DE.is_connected(grid, start_x, start_y):
                print(f"Maze connected on attempt {map_attempts} and iteration {iteration}.")

                # Testing placing random tile
                if lvl == 2 and maps_data is not None:
                    map0_grid = maps_data[0]["grid"]
                    potential_coords = [
                        (x, y) for x in range(grid_size) for y in range(grid_size)
                        if map0_grid[x][y] in {PATH, HIDDEN}
                    ]

                    for x, y in potential_coords:
                        surrounding_empty = all(
                            0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY
                            for nx, ny in [
                                (x - 1, y), (x + 1, y),
                                (x, y - 1), (x, y + 1),
                                (x - 1, y - 1), (x - 1, y + 1),
                                (x + 1, y - 1), (x + 1, y + 1)
                            ]
                        )

                        if surrounding_empty:
                            grid[x][y] = PATH
                            print(f"Placed PATH on level 2 at ({x}, {y}) based on level 0.")
                            break

                return grid, descending_coords
            else:
                print(f"Maze not connected. Refining... (Map Attempt {map_attempts}, Iteration {iteration + 1})")
                DE.refine_map(grid)
                iteration += 1

        print(f"Map attempt {map_attempts} failed after {max_iterations} iterations. Generating a new map...")

    raise RuntimeError(f"Unable to generate a connected labyrinth after {max_map_attempts} attempts.")


def save_floor_image(grid, output_image_path):
    image = Image.new("RGB", (grid_size, grid_size), value_to_color[EMPTY])
    pixels = image.load()

    for x in range(grid_size):
        for y in range(grid_size):
            pixels[x, y] = value_to_color[grid[x][y]]

    image.save(output_image_path)
    print(f"Generated image: {output_image_path}")


def run(nb_lvl, maze_type="voronoi", generate_bin=False):
    if maze_type not in ["maze", "road", "voronoi", "shuffle"]:
        raise ValueError('maze_type must be "maze", "road", "voronoi", "shuffle"')

    maps_data = []
    descending_coords = None

    for i in range(nb_lvl):
        grid, descending_coords = generate_floor_data(
            lvl=i,
            maps_data=maps_data
        )
        maps_data.append({"level": i, "grid": grid})

    for data in maps_data:
        lvl = data["level"]
        grid = data["grid"]
        output_image_path = os.path.join(output_dir, f"Map_m{lvl}.png")
        save_floor_image(grid, output_image_path)

        if generate_bin:
            DE.reconstruct_bin(lvl=lvl, image_path=output_image_path, output_directory=output_dir)
            print(f"Binary and image files {lvl}: {output_dir} folder.")


if __name__ == "__main__":
    run(nb_lvl=3, maze_type="shuffle", generate_bin=False)
