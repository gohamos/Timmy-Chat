import streamlit as st
import time
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))
st.set_page_config(page_title="Methodology", page_icon="👨")
contentfile = "content/Method.xml"

from logics.pagecontent import pagecontent
pagecontent(contentfile)
