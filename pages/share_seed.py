import os
import pandas as pd
import zipfile
import shutil
import streamlit as st
from PIL import Image
from utils.page_config import page_config
import DungeonEncounters as DE


def parse_saved_seed_dir(directory):
    data = []
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        subfolder_100p = os.path.join(folder_path, "100p")
        if os.path.isdir(folder_path) and os.path.isdir(subfolder_100p):
            try:
                maze_type, seed, param, cheat = folder.split("_")
                data.append({
                    "Seed": seed,
                    "Maze Type": maze_type,
                    "Setting": param,
                    "Cheat Mode": "✅" if cheat == "cheat" else "❌",
                    "Folder Path": folder_path,
                })
            except ValueError:
                continue
    return data


def show_details(folder_path, seed, maze_type, cheat_mode, param_1):
    subfolder_720p = os.path.join(folder_path, "720p")
    subfolder_100p = os.path.join(folder_path, "100p")
    st.subheader(f"Seed: {seed} | Maze Type: {maze_type} | Setting: {param_1} | Cheat Mode: {cheat_mode}")
    col1, col2 = st.columns([2, 1])
    if os.path.isdir(subfolder_720p):
        files_720p = [os.path.join(subfolder_720p, f) for f in os.listdir(subfolder_720p) if f.endswith((".png", ".jpg"))]

        if files_720p:
            tabs = col1.tabs([os.path.basename(file_path) for file_path in files_720p])
            for i, file_path in enumerate(files_720p):
                with tabs[i]:
                    image = Image.open(file_path)
                    st.image(image, caption=f"{os.path.basename(file_path)}")
        else:
            st.warning("No images found in the 720p folder.")
    else:
        st.warning(f"No 720p folder found in {folder_path}")

    zip_file_path = os.path.join(folder_path, f"{maze_type}_{seed}_{param_1}_{'nocheat' if cheat_mode == '❌' else 'cheat'}.zip")
    if not os.path.exists(zip_file_path):
        with st.spinner("Creating .bin files..."):
            for i in range(100):
                output_image_path = os.path.join(subfolder_100p, f"Map_m{i}.png")
                DE.reconstruct_bin(lvl=i, image_path=output_image_path, output_directories=[subfolder_100p])

        with st.spinner("Creating ZIP file..."):
            zipf = zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED)

            if os.path.isdir(subfolder_100p):
                for root, dirs, files in os.walk(subfolder_100p):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), start=folder_path))

            if os.path.isdir(subfolder_720p):
                for root, dirs, files in os.walk(subfolder_720p):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), start=folder_path))

            zipf.close()

    with open(zip_file_path, "rb") as f:
        col2.download_button(label="💾 Download maps and .bin files", data=f, mime="application/zip",
                             file_name=f"{maze_type}_{seed}_{'nocheat' if cheat_mode == '❌' else 'cheat'}.zip")

    st.divider()


page_config(logo=True)
st.title("Community Seeds 🌱")
st.success(
    "Welcome to the Community Seeds Tab! 🌱 Here, you'll find Seeds created by players (only if all 100 levels have been generated). "
    "You can view them by checking the boxes in the 'Show' column and download the maps along with .bin files. 'Setting' is the generation parameter (Depth, Empty Width, Node Number)."
    "\n\nIf nothing appears, the Streamlit server may have restarted, and the files were cleared. More information is available on the main page.")

saved_seed_dir = "saved_seed"
if not os.path.exists(saved_seed_dir):
    os.makedirs(saved_seed_dir)
if len(os.listdir(saved_seed_dir)) > 0:
    seed_data = parse_saved_seed_dir(saved_seed_dir)

    df = pd.DataFrame(seed_data)
    df = df.drop(columns=["Folder Path"])

    dt_st1, sf_st2 = st.columns([1, 2])
    maze_types = ["Maze", "Road", "Voronoi", "Shuffle"]
    selected_types = dt_st1.multiselect("Filter Maze Types", options=maze_types, default=maze_types,
                                        help="Select the maze types you want to include in the table.")

    if selected_types:
        selected_types_lower = [type.lower() for type in selected_types]
        df = df[df["Maze Type"].str.lower().isin(selected_types_lower)]

    cheat_filter = dt_st1.radio("Filter Cheat Mode", options=["Yes", "No", "Both"], index=2,
                                help="Filter by cheat mode status.", horizontal=True)

    if cheat_filter == "Yes":
        df = df[df["Cheat Mode"] == "✅"]
    elif cheat_filter == "No":
        df = df[df["Cheat Mode"] == "❌"]

    if not df.empty:
        df["Show"] = False

        edited_df = sf_st2.data_editor(df, use_container_width=True, hide_index=True)
        st.divider()

        for index, row in edited_df.iterrows():
            if row["Show"]:
                folder_path = os.path.join(saved_seed_dir, f"{row['Maze Type']}_{row['Seed']}_{row["Setting"]}_{'nocheat' if row['Cheat Mode'] == '❌' else 'cheat'}")
                show_details(folder_path, row["Seed"], row["Maze Type"], row["Cheat Mode"], row["Setting"])
    else:
        sf_st2.warning("No saved seeds found. 😓")
