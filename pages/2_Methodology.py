import streamlit as st
import time
import numpy as np
import os

# Change the working directory to the current file's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"The current working directory is: {os.getcwd()}")

st.set_page_config(page_title="About Us", page_icon="👨")

st.markdown("# Methodology")
st.sidebar.header("Methodology")
st.write(
    """Methodology <to-complete>"""
)

st.image("images/timmy_method.jpg", caption= "Data Flow of the TIMMY app")
