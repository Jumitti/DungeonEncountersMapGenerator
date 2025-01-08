import streamlit as st
import os


def page_config(logo=None):
    if st.get_option("client.showSidebarNavigation") is True:
        st.set_option("client.showSidebarNavigation", False)
        st.rerun()

    img_path = os.path.join(os.path.dirname(__file__), '../.streamlit', 'DE_icon.jpg')

    st.set_page_config(page_title='Dungeon Encounters Map Generator', page_icon=img_path,
                       initial_sidebar_state="expanded", layout="wide")

    st.logo(img_path)
    if logo is True:
        st.sidebar.image(img_path)
    st.sidebar.title('🧱 DE Map Generator')
    st.sidebar.write("Created by [Minniti Julien](https://github.com/Jumitti)")
    st.sidebar.page_link("DEMG_streamlit.py", label="**Home / Generator**", icon="🏠")
    st.sidebar.page_link("pages/share_seed.py", label="Community Seed", icon="🌱")
    st.sidebar.divider()

