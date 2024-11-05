# Set up and run this Streamlit App
import streamlit as st


import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


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

