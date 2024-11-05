import streamlit as st
import time
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))
st.set_page_config(page_title="About Us", page_icon="👨")
contentfile = "content/About.xml"

from logics.pagecontent import pagecontent
pagecontent(contentfile)

