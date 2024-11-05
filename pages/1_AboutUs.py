import streamlit as st
import time
import numpy as np
import os

st.set_page_config(page_title="About Us", page_icon="👨")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import xmltodict
contentfile = "content/About.xml"
with open(contentfile,mode='r') as f:
    #print("[] reading file",contentfile,flush=True)
    try:
        mycontent=xmltodict.parse(f.read())       
        for section in mycontent["content"]["sections"]["section"]:
            if "title" in section:
                st.title(section["title"])
                st.sidebar.header(section["title"])
            if "text" in section:
                st.write(section["text"])
            if "tablefile" in section:
                import pandas as pd
                tablefile = section["tablefile"]
                stepsdf = pd.read_csv(tablefile)
                st.table(tablefile)
            if "image" in section:
                caption=""                
                if "caption" in section:
                    caption = section["caption"]
                st.image(section["image"], caption= caption)
    except Exception as e:
        print("\t!!",e,flush=True)


