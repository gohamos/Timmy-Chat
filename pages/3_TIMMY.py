# Set up and run this Streamlit App
import streamlit as st

import os

# Change the working directory to the current file's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"The current working directory is: {os.getcwd()}")



from logics.check_password import check_password
if not check_password():
    st.stop()  # Do not continue if check_password is not True.




from logics.load_llm import getLLM




# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="Project TIMMY"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("Project TIMMY App")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
#for message in st.session_state.messages:
#    with st.chat_message(message["role"]):
#        st.markdown(message["content"])


issetup = 0
#First message
with st.chat_message("assistant"):    
    llm=getLLM()
    if llm is None:
        st.write("ERROR! Unable to load LLM. Please check on your API environment")
        exit()
    else:    
        st.write("> Loading Database ......")    
        from logics.test_agent import response
        from logics.test_agent import databasesize
        if databasesize()>0:
            st.write("> Database loaded.")    
            st.write("Hello, how may I help you today?") 
            issetup=1        
        else:
            st.write("ERROR! Unable to load Database.")
            exit()
            
 
# React to user input
persistdebug=0
if issetup> 0:
    if prompt := st.chat_input("Enter your query here."):
        if "<DEBUG ON>" in prompt:
            persistdebug=2
            prompt = prompt.replace("<DEBUG ON>","")
        elif "<DEBUG OFF>" in prompt:
            persistdebug=0
            prompt = prompt.replace("<DEBUG OFF>","")
        printdebug = persistdebug
        if "<DEBUG>" in prompt:
            printdebug=2
            prompt = prompt.replace("<DEBUG>","")
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.status("Checking Database..."):
            st.write("Searching for data")
            answer = response(prompt,printdebug=printdebug)
            if "!!" in answer[0]:
                st.write("Error in Search!")
            else:
                st.write("Data Found!")
                
                
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.write(f"{answer[0]}")
            st.write("What else may I help you with today?")
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer[0]})




