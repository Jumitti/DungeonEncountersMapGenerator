import streamlit as st
import generate_maps
import os
import shutil
from PIL import Image
import zipfile

output_dir = "output"
output_dir_720p = "output_720p"
zip_path = None

os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_dir_720p, exist_ok=True)

st.set_page_config(
    page_title='Dungeon Encounters Map Generator',
    page_icon=".streamlit/DE_icon.jpg",
    initial_sidebar_state="expanded",
    layout="wide"
)

st.logo(".streamlit/DE_icon.jpg")

if "output_files_720p" not in st.session_state:
    st.session_state["output_files_720p"] = []
if "zip_path" not in st.session_state:
    st.session_state["zip_path"] = None
if "generated" not in st.session_state:
    st.session_state["generated"] = False

st.title("Dungeon Encounters Map Generator")

with st.expander("**Welcome to the Dungeon Encounters Map Generator!**"):
    st.success(r"""
        This generator creates dungeon maps for the game *Dungeon Encounters*. It allows you to create mazes, roads, or random maps with customizable options.
    
        **Generation Parameters:**
        - **Generation Type**: Choose the type of map to generate:
            - *Maze*: A classic maze with narrow paths.
            - *Road*: A map with open roads and intersections.
            - *Voronoi*: A generation type based on Voronoi diagrams, creating irregular zones.
            - *Shuffle*: A mixed map type, with varied generation elements.
        - **Depth, Empty Width, Node Number**: These parameters adjust the map generation characteristics based on the selected type.
    
        **Cheat Mode:**
        - By enabling *cheat_mode*, all treasures, combat abilities, and movement skills will be placed on level 0, providing immediate access to all resources in the game.
    
        **After Generation:**
        - Once the maps are generated, the `.bin` files should be placed in the following directory:
          - `C:\Program Files (x86)\Steam\steamapps\common\DUNGEON ENCOUNTERS\DUNGEON ENCOUNTERS_Data\StreamingAssets\xlsx`
          - Note: The directory path may vary depending on where your game is installed.
    
        **Important Reminder:**
        - I do not take responsibility for any issues that may arise. I strongly recommend making a backup of your maps before replacing any files in the game directory.
    
        **Generation Delays and Errors:**
        - Sometimes, map generation can be slow, especially for larger maps. If you encounter a `max_attempts` error, don’t be alarmed—it’s simply due to the time taken for the generation process. Just restart the generation, and it should work fine.
        - Over time, I will continue to fix and improve any bugs, so please be patient and feel free to report any issues you encounter.
    
        This generator is perfect for creating custom maps for your Dungeon Encounters adventures. You can choose the map type, adjust parameters, and see the results in real time!
    """)

st.sidebar.image(".streamlit/DE_icon.jpg")
st.sidebar.header("Generation settings")
nb_levels = st.sidebar.number_input("Number of levels", min_value=1, max_value=100, value=5)
maze_type = st.sidebar.selectbox("Type of maze", ["Maze", "Road", "Voronoi", "Shuffle"], index=2)

if maze_type == "Maze":
    param_label = "Depth"
    param_min = 1
    param_max = 1000
    param_value = 50
elif maze_type == "Road":
    param_label = "Empty Width"
    param_min = 1
    param_max = 40
    param_value = 15
elif maze_type == "Voronoi":
    param_label = "Node Number"
    param_min = 5
    param_max = 250
    param_value = 25

if maze_type in ["Maze", "Road", "Voronoi"]:
    param_value = st.sidebar.slider(param_label, min_value=param_min, max_value=param_max, value=param_value, step=1)
else:
    param_value = None

cheat_mode = st.sidebar.checkbox("Cheat Mode", value=False)
generate_bin = st.sidebar.checkbox("Generate .bin files", value=False)


def clean_output_dirs():
    for folder in [output_dir, output_dir_720p]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                st.error(f"Cleaning error {file_path}: {e}")


sd_col1, sd_col2 = st.sidebar.columns(2)

if sd_col1.button(f"Preview Map_{nb_levels - 1}"):
    clean_output_dirs()

    try:
        generate_maps.run_streamlit(nb_lvl=None, maze_type=maze_type.lower(), generate_bin=generate_bin,
                                    param_1=param_value, cheat_mode=cheat_mode, one_lvl=[nb_levels - 1])
        st.success("Generation successfully completed!")

        st.session_state["output_files_720p"] = sorted(
            [os.path.join(output_dir_720p, f) for f in os.listdir(output_dir_720p) if f.endswith(".png")]
        )
        st.session_state["generated"] = True

    except Exception as e:
        st.error(e)

if sd_col2.button(f"Generate maps (0 to {nb_levels - 1})"):
    clean_output_dirs()

    try:
        generate_maps.run_streamlit(nb_lvl=nb_levels, maze_type=maze_type.lower(), param_1=param_value,
                                    generate_bin=generate_bin, cheat_mode=cheat_mode)
        st.success("Generation successfully completed!")

        st.session_state["output_files_720p"] = sorted(
            [os.path.join(output_dir_720p, f) for f in os.listdir(output_dir_720p) if f.endswith(".png")]
        )
        st.session_state["generated"] = True

        st.session_state["zip_path"] = os.path.join(output_dir, "generated_maps.zip")
        with zipfile.ZipFile(st.session_state["zip_path"], "w") as zipf:
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path) and file != "generated_maps.zip":
                    zipf.write(file_path, arcname=os.path.join("original", file))

            for file in os.listdir(output_dir_720p):
                file_path = os.path.join(output_dir_720p, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=os.path.join("720p", file))

    except Exception as e:
        st.error(e)


if st.session_state["generated"] and st.session_state["output_files_720p"]:
    tabs = st.tabs([os.path.basename(file_path) for file_path in st.session_state["output_files_720p"]])
    for i, file_path in enumerate(st.session_state["output_files_720p"]):
        with tabs[i]:
            image = Image.open(file_path)
            st.image(image, caption=f"{os.path.basename(file_path)}")

if st.session_state["zip_path"] and os.path.exists(st.session_state["zip_path"]):
    with open(st.session_state["zip_path"], "rb") as f:
        st.sidebar.download_button(
            label="Download maps and .bin files",
            data=f,
            file_name="generated_maps.zip",
            mime="application/zip"
        )
