# Set up and run this Streamlit App
import streamlit as st


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Project TIMMY 👋")

st.sidebar.success("Page selection above ")

st.markdown(
    """
    Project TIMMY (Transport Incident Master Made for You) is a chatbot created to help the LTA ITSSD Team to query and gain insights from the incident reports database.

"""
)

