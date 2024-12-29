# Dungeon Encounters Map Generator

This project generates maps for the game **Dungeon Encounters**, developed and published by **Square Enix**. It's a tool I created to reproduce the game's maps, reversing the maze generation process and allowing the manipulation of certain game elements.

**Important Note**: This project relies on reverse engineering of the game files to understand the structure and recreate the maps. I am not responsible for any legal consequences arising from the use of this project.

## Legal Disclaimer

The game **Dungeon Encounters** is the property of **Square Enix** and its associated partners. This project is an attempt to recreate some of the game's maps for personal use. It is important to note that using this project may violate the terms and conditions of the game. I recommend that you use it for personal purposes only, and do not redistribute modified files.

I accept no responsibility for any legal consequences arising from the use of this project, particularly with regard to the game's copyright and trademarks.

## Project Objective

The aim of this project is to enable users to generate **Dungeon Encounters** maps by reusing the game files. The reverse process involves analyzing existing maps and reconstructing mazes based on the extracted data.

### Features:

- **Map Generation**: The script recreates mazes following the logic of the game.
- **Placement of Wanderers**: You can place characters ("Wanderers") on the map according to their coordinates.
- **Creation of .bin Files**: Generates binary files from the created maps.

## Installation

1. Download the project and place it in a directory of your choice.
2. Make sure you have Python installed on your machine (version 3.x recommended).
3. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the generated `.bon` files into the following directory of your **Dungeon Encounters** installation:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\DUNGEON ENCOUNTERS\DUNGEON ENCOUNTERS_Data\StreamingAssets\xlsx
   ```

**Note**: I haven't tested this script with other versions of the game, so it may not work with versions other than the one mentioned.

## Usage

1. **Run the script**: Once the necessary files are in place, run the Python script to generate the maps.
   ```bash
   python generate_maps.py
   ```

2. **Generate Mazes**: The script will create image and binary files for each floor of the game. You can use these in your own instance of the game.

3. **Modify Maps**: If you wish to customize the maps, you can modify the configuration files to adjust the parameters of the generated mazes.

## Acknowledgements

- **Square Enix** for the creation of **Dungeon Encounters**.
