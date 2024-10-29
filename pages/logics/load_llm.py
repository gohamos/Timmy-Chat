from openai import OpenAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

if 'client' not in globals():
    client = None
if 'llm' not in globals():
    llm = None
   
if llm is None:    
    envpath = ["./", "../","../../","../../../"]
    envfile = [".env", "env",]
    loaded = 0
    for dir in envpath:
        for file in envfile:
            if os.path.isfile(dir+file):
                print("[] Loading environment from ",dir+file)
                load_dotenv(dir+file)
                loaded=1
                break
        if loaded>0:
            break;
           
    
    if loaded>0:
        OPENAI_API_KEY= os.getenv('OPENAI_API_KEY')
        OPENAI_MODEL_NAME= os.getenv('OPENAI_MODEL_NAME')
        OPENAI_BASE_URL= os.getenv('OPENAI_BASE_URL')
    else:             
        OPENAI_API_KEY=None
        OPENAI_MODEL_NAME=None
        OPENAI_BASE_URL=None       
        try:
            print("[] Loading secrets ")
            import streamlit as st
            OPENAI_API_KEY= st.secrets['OPENAI_API_KEY']
            print("[] Loadedsecrets OPENAI_API_KEY")
            OPENAI_MODEL_NAME= st.secrets['OPENAI_MODEL_NAME']
            print("[] Loaded secrets OPENAI_MODEL_NAME")
            loaded=1
            OPENAI_BASE_URL= st.secrets['OPENAI_BASE_URL']
            print("[] Loaded secrets OPENAI_BASE_URL")
        except:
            dummy=1

        if loaded ==0:
            try:
                print(st.secrets, flush=True)
            except:
                dummy=1
            
    
            
    if (OPENAI_API_KEY) is None:
        print("!! ERROR, Cannot load OPENAI_API_KEY")
    elif (OPENAI_MODEL_NAME) is None:
        print("!! ERROR, Cannot load OPENAI_MODEL_NAME")
    elif len(OPENAI_API_KEY)==0:
        print(" !! ERROR, OPEN AI_KEY_Not Specified!")        
    elif len(OPENAI_API_KEY)==0:
        print(" !! ERROR, OPEN AI_KEY_Not Specified!")
    else:
        print(f'OPENAI_API_KEY    = {OPENAI_API_KEY}')
        print(f'OPENAI_MODEL_NAME = {OPENAI_MODEL_NAME}')
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("[] OpenAI Client Opened ",client)
        if (OPENAI_BASE_URL) is None or len(OPENAI_BASE_URL)==0:
            llm=ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL_NAME)
        else:
            print(f'OPENAI_BASE_URL = {OPENAI_BASE_URL}')
            llm=ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL_NAME, base_url=OPENAI_BASE_URL)
            
        print("[] LLM  Client Opened ",llm)



def getLLM():
    return llm

def getClient():
    return client


