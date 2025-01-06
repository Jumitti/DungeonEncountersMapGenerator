# Dungeon Encounters Map Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dungeon-encounters-map-generator.streamlit.app/)

This project generates maps for the game **Dungeon Encounters**, developed and published by **Square Enix**. It's a tool I created to reproduce the game's maps, reversing the maze generation process and allowing the manipulation of certain game elements.

**Important Note**: This project relies on reverse engineering of the game files to understand the structure and recreate the maps. I am not responsible for any legal consequences arising from the use of this project.

## Legal Disclaimer

The game **Dungeon Encounters** is the property of **Square Enix** and its associated partners. This project is an attempt to recreate some of the game's maps for personal use. It is important to note that using this project may violate the terms and conditions of the game. I recommend that you use it for personal purposes only, and do not redistribute modified files.

I accept no responsibility for any legal consequences arising from the use of this project, particularly with regard to the game's copyright and trademarks.

## Project Objective

The aim of this project is to enable users to generate **Dungeon Encounters** maps by reusing the game files. The reverse process involves analyzing existing maps and reconstructing mazes based on the extracted data.

### Features:

- **Map Generation**: The script recreates mazes following the logic of the game.
- **Seed Generation**: Use seeds (like in Minecraft) (LIMIT: seeds are permanently used, but if you set "shuffle", the type of maps will still be random)
- **Creation of .bin Files**: Generates binary files from the created maps.
- **Cheat Mode**: By enabling cheat mode, all treasures, combat abilities, and movement skills will be placed on level 0 for immediate access.

## Streamlit Version

In addition to the Python script, a **Streamlit** web app version is available for an easier, interactive experience. The Streamlit version allows you to generate maps and adjust parameters in real time. You can access it via this [link](https://dungeon-encounters-map-generator.streamlit.app/).

## Installation

1. Download the project and place it in a directory of your choice.  
2. Make sure you have Python installed on your machine (version 3.x recommended).  
3. Install the necessary dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
4. Optionally, run the Streamlit app for a user-friendly interface:  
   ```bash
   streamlit run DEMG_streamlit.py
   ```  

## Where to Place the `.bin` Files

After generating the `.bin` files, copy them to the following directory in your **Dungeon Encounters** installation:  
```
C:\Program Files (x86)\Steam\steamapps\common\DUNGEON ENCOUNTERS\DUNGEON ENCOUNTERS_Data\StreamingAssets\xlsx
```  

**Note**: This tool has been tested with the Steam version of the game. Compatibility with other versions may vary.  


## Important Reminder

- **Generation Delays and Errors**: Sometimes, map generation can be slow, especially for larger maps. If you encounter a `max_attempts` error, don’t be alarmed—it’s simply due to the time taken for the generation process. Just restart the generation, and it should work fine. Over time, I will continue to fix and improve any bugs, so please be patient and feel free to report any issues you encounter.

- **Backup**: I do not take responsibility for any issues that may arise. I strongly recommend making a backup of your maps before replacing any files in the game directory.

## Acknowledgements

- **Square Enix** for the creation of **Dungeon Encounters**.
- **Exvaris (Reddit) et al.** for **[Compendium Project](https://docs.google.com/spreadsheets/d/1JCgdir76fjPvVMQwX287lc5BCNiZY6fA/edit?gid=313293529#gid=313293529)**
- **gomtuu123 (Reddit)** for **[Interactive Map](https://gomtuu.org/dungeon-enc/#settings)**
- **[r/DungeonEncounters](https://www.reddit.com/r/DungeonEncounters/)**