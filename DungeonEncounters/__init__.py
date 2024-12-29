import json
import random
import numpy as np
from collections import deque
from random import shuffle, choice
from scipy.spatial import Voronoi, voronoi_plot_2d

from PIL import Image


def reconstruct_bin(image_path, json_path, output_bin_path):
    image = Image.open(image_path)
    pixels = image.load()

    with open(json_path, "r") as f:
        special_cases = json.load(f)

    width, height = image.size
    if width != 100 or height != 100:
        raise ValueError("Image size must be 100x100 pixels.")

    with open(output_bin_path, "wb") as f:
        for y in range(100):
            for x in range(100):
                r, g, b = pixels[x, y]

                hex_value = None
                for key, case in special_cases.items():
                    if case["color"] == [r, g, b]:
                        hex_value = int(key, 16)
                        break

                if hex_value is None:
                    raise ValueError(f"No value found for color {r, g, b} at position ({x}, {y})")

                f.write(hex_value.to_bytes(3, 'big'))

    print(f"The {output_bin_path} file has been generated successfully.")


def is_valid_move(grid, x, y, dx, dy, EMPTY=next(
    (int(key, 16) for key, case in json.load(open("special_case.json")).items() if case["name"] == "EMPTY"), None),
                  grid_size=100):
    for i in range(5, 20):
        nx, ny = x + dx * i, y + dy * i
        if not (0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == EMPTY):
            return False
    return True


def generate_maze(grid, x, y, max_depth=50, CASE=next(
    (int(key, 16) for key, case in json.load(open("special_case.json")).items() if case["name"] == "CASE"), None),
                  grid_size=100):
    if max_depth <= 0:
        return

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)

    for dx, dy in directions:
        if is_valid_move(grid, x, y, dx, dy):
            for i in range(1, 5):
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    grid[nx][ny] = CASE
            generate_maze(grid, nx, ny, max_depth - 1)


def generate_random_routes(grid, grid_size=100, x=50, y=50, route_width=3,
                           CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                      case["name"] == "CASE"), None),
                           EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                       case["name"] == "EMPTY"), None)):
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
            for i in range(route_width):
                if 0 <= nx - i < grid_size:
                    grid[nx - i][ny] = CASE
                if 0 <= ny - i < grid_size:
                    grid[nx][ny - i] = CASE

            for neighbor in neighbors(nx, ny):
                if grid[neighbor[0]][neighbor[1]] == EMPTY:
                    frontier.append(neighbor)
            shuffle(frontier)

    return grid


def generate_voronoi_map(grid, start_x, start_y, grid_size=100, num_sites=200,
                         CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                    case["name"] == "CASE"), None),
                         EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                     case["name"] == "EMPTY"), None)
                         ):
    half_grid_size = grid_size // 2

    min_x = max(0, start_x - half_grid_size)
    max_x = min(len(grid), start_x + half_grid_size + max(0, - (start_x - half_grid_size)))

    min_y = max(0, start_y - half_grid_size)
    max_y = min(len(grid[0]), start_y + half_grid_size + max(0, - (start_y - half_grid_size)))

    sites = np.array([[start_x, start_y]] + [[
        random.randint(min_x, max_x - 1),
        random.randint(min_y, max_y - 1)
    ] for _ in range(num_sites - 1)])

    vor = Voronoi(sites)

    for ridge in vor.ridge_vertices:
        if -1 in ridge:
            continue
        start, end = vor.vertices[ridge]
        start = np.round(start).astype(int)
        end = np.round(end).astype(int)

        if (0 <= start[0] < len(grid) and 0 <= start[1] < len(grid[0]) and
                0 <= end[0] < len(grid) and 0 <= end[1] < len(grid[0])):
            for x, y in bresenham_line(start[0], start[1], end[0], end[1]):
                if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
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


def is_connected(grid, start_x, start_y,
                 CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                            case["name"] == "CASE"), None),
                 EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                             case["name"] == "EMPTY"), None),
                 grid_size=100):
    visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]
    stack = [(start_x, start_y)]

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    visited[start_x][start_y] = True
    visited_count = 1

    while stack:
        x, y = stack.pop()

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < grid_size and 0 <= ny < grid_size and not visited[nx][ny] and grid[nx][ny] != EMPTY:
                visited[nx][ny] = True
                stack.append((nx, ny))
                visited_count += 1

    total_non_empty_count = sum(cell != EMPTY for row in grid for cell in row)
    return visited_count == total_non_empty_count


def remove_random_paths(grid, percentage_to_remove,
                        CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                   case["name"] == "CASE"), None),
                        EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                                    case["name"] == "EMPTY"), None), grid_size=100):
    paths = [(x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] == CASE]
    random.shuffle(paths)

    num_to_remove = int(len(paths) * percentage_to_remove)
    start_x, start_y = next((x, y) for x in range(grid_size) for y in range(grid_size) if grid[x][y] == CASE)

    for i in range(num_to_remove):
        x, y = paths[i]
        to_remove = [(x, y)]
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == CASE:
                to_remove.append((nx, ny))
                if len(to_remove) == 5:
                    break

        removed_cases = []
        for rx, ry in to_remove:
            grid[rx][ry] = EMPTY
            removed_cases.append((rx, ry))

        visited = set()
        dfs(grid, start_x, start_y, visited)

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
    visited = set()
    queue = deque([(x, y, [])])
    visited.add((x, y))

    if case_type == "RANDOM":
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
            for px, py in path:
                if grid[px][py] == EMPTY:
                    grid[px][py] = target_case
            return path

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0),
                       (1, -1), (-1, 1), (1, 1), (-1, -1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] in [EMPTY, CASE] and (
                    nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))


def refine_map(grid, grid_size=100,
               CASE=next((int(key, 16) for key, case in json.load(open("special_case.json")).items()
                          if case["name"] == "CASE"), None),
               EMPTY=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                           case["name"] == "EMPTY"), None),
               HIDDEN=next((int(key, 16) for key, case in json.load(open("special_case.json")).items() if
                            case["name"] == "HIDDEN"), None)):
    for x in range(1, grid_size - 1):
        for y in range(1, grid_size - 1):
            if grid[x][y] != EMPTY:
                value_case = grid[x][y]
                special_cases = {
                    int(key, 16): case["name"]
                    for key, case in json.load(open("special_case.json")).items()
                }

                case_name = special_cases.get(value_case, "UNKNOWN")

                if (grid[x - 1][y] == EMPTY and grid[x + 1][y] == EMPTY and
                        grid[x][y - 1] == EMPTY and grid[x][y + 1] == EMPTY and
                        grid[x - 1][y - 1] == EMPTY and grid[x - 1][y + 1] == EMPTY and
                        grid[x + 1][y - 1] == EMPTY and grid[x + 1][y + 1] == EMPTY):

                    grid[x][y] = EMPTY
                    complete_path_with_hidden(grid, x, y, "RANDOM")
                    grid[x][y] = value_case

                elif (grid[x - 1][y] == EMPTY and grid[x + 1][y] == EMPTY and
                      grid[x][y - 1] == EMPTY and grid[x][y + 1] == EMPTY):
                    if case_name not in ['CASE', "HIDDEN"]:
                        value_case = HIDDEN

                    if grid[x - 1][y - 1] != EMPTY:
                        grid[x - 1][y] = value_case
                    elif grid[x - 1][y + 1] != EMPTY:
                        grid[x - 1][y] = value_case
                    elif grid[x + 1][y - 1] != EMPTY:
                        grid[x + 1][y] = value_case
                    elif grid[x + 1][y + 1] != EMPTY:
                        grid[x + 1][y] = value_case

                elif ((grid[x - 1][y] != EMPTY and
                       grid[x + 1][y] == EMPTY and grid[x][y - 1] == EMPTY and grid[x][y + 1] == EMPTY) or
                      (grid[x + 1][y] != EMPTY and
                       grid[x - 1][y] == EMPTY and grid[x][y - 1] == EMPTY and grid[x][y + 1] == EMPTY) or
                      (grid[x][y - 1] != EMPTY and
                       grid[x - 1][y] == EMPTY and grid[x + 1][y] == EMPTY and grid[x][y + 1] == EMPTY) or
                      (grid[x][y + 1] != EMPTY and
                       grid[x - 1][y] == EMPTY and grid[x + 1][y] == EMPTY and grid[x][y - 1] == EMPTY)):

                    if grid[x - 1][y] != EMPTY:
                        if grid[x + 1][y - 1] != EMPTY:
                            grid[x][y - 1] = value_case
                        elif grid[x + 1][y + 1] != EMPTY:
                            grid[x][y + 1] = value_case

                    elif grid[x + 1][y] != EMPTY:
                        if grid[x - 1][y - 1] != EMPTY:
                            grid[x][y - 1] = value_case
                        elif grid[x - 1][y + 1] != EMPTY:
                            grid[x][y + 1] = value_case

                    elif grid[x][y - 1] != EMPTY:
                        if grid[x - 1][y + 1] != EMPTY:
                            grid[x - 1][y] = value_case
                        elif grid[x + 1][y + 1] != EMPTY:
                            grid[x + 1][y] = value_case

                    elif grid[x][y + 1] != EMPTY:
                        if grid[x - 1][y - 1] != EMPTY:
                            grid[x - 1][y] = value_case
                        elif grid[x + 1][y - 1] != EMPTY:
                            grid[x + 1][y] = value_case
