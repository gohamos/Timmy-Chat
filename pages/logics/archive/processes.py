import os
import pandas as pd
from langchain.agents import Tool
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from crewai import Agent, Task, Crew

from pages.logics.crews import run_crew_0, run_crew_0b, run_crew_1
from pages.logics.load_data import loadfiles, loadLookup

##### NOTE This script assumes you have already run test_loadingofcsv.py to generate the "output" directory of preprocessed tables (replaces values in tables with lookup descriptions, removes invalid timestamps etc.) 


envpath = [".env", "env"]
# Change the working directory to the current file's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"The current working directory is: {os.getcwd()}")
for envfile in envpath:
    if os.path.isfile(envfile):
        load_dotenv(envfile)
        break
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
if (OPENAI_API_KEY) is None:
    print("!!Cannot load OPENAI_API_KEY")
    exit()
    if len(OPENAI_API_KEY)==0:
        exit()
        
OPENAI_MODEL_NAME=os.getenv('OPENAI_MODEL_NAME')
if (OPENAI_MODEL_NAME) is None:
    print("!!Cannot load OPENAI_MODEL_NAME")
    exit()
    if len(OPENAI_MODEL_NAME)==0:
        exit()

        
print(f'OPENAI_API_KEY    = {OPENAI_API_KEY}')
print(f'OPENAI_MODEL_NAME = {OPENAI_MODEL_NAME}')
#print(f'OPENAI_API_BASE = {OPENAI_API_BASE}')

filterCols=["UP_POINT","DN_POINT","UP_LINK_ID","DN_LINK_ID","START_X_COOR","START_Y_COOR","END_X_COOR","END_Y_COOR","Q_END_X_COOR","Q_END_Y_COOR","TUNNEL_X","TUNNEL_Y"]

if os.path.isdir("outpickle"):
    filelist = loadfiles(dir="outpickle",printdebug=2,subdir=0,reparse=0,filtercols=filterCols,filtertime=0,formattime=0)
else:
    filelist = loadfiles(dir="output",printdebug=2,subdir=0,reparse=0,filtercols=filterCols,filtertime=0,formattime=0)

DictMap ,EwayDict =loadLookup(dir="output",printdebug=1,subdir=1)

#recordlist=mergingRecords(filelist,printdebug=1)
#print(len(recordlist))

from langchain.agents import Tool



# Creating tool_agents (From 3rd party)
pandas_tool_agent = create_pandas_dataframe_agent(
    llm=ChatOpenAI(temperature=0, #openai_api_base=OPENAI_API_BASE,
                    model = OPENAI_MODEL_NAME,
                    ),
    df = list(filelist.values()), #list of panda dataframe
    agent_type=AgentType.OPENAI_FUNCTIONS,# <-- This is an "acknowledgement" that this can run potentially dangerous code
    allow_dangerous_code=True
)

# Create the tool
pandas_tool = Tool(
    name="Search and Analyze tabular data with Code",
    func=pandas_tool_agent.invoke, # <-- This is the function that will be called when the tool is run. Note that there is no `()` at the end
    description="Useful for search-based queries.",
)

columns_description = os.getenv("COLUMNS_DESCRIPTION")

for col in filterCols:
    if col in columns_description:
        del columns_description[col]
        
for col in columns_description:
    if col in DictMap:
        columns_description[col]=columns_description[col]+" Possible Values:"+",".join(DictMap[col].values())

columnstr = (str)(columns_description)

def respond(prompt_1):
    print()
    system_user_message = f"""You have access to a number of pandas dataframes. These pandas dataframes contain the traffic incident records from Land Transport Authority. \
    the datafranes uses columns with descriptions delimited by the following json enclosed in <column> enclosed tags:
    <columns>{columns_description}</columns>    

    All dates are in Day/Month/Year format

    Understand the question delimited by a pair of <text> enclosed and search the dataframes for relevant data within the provided context and give an accurate answer.
    Don't assume you have access to any libraries other than built-in Python ones and pandas. \
    Make sure to refer only to the dataframes mentioned above.

    Question: <text>{prompt_1}</text>"""
    print("-- Query=",prompt_1)
    print("[] Calling crew0",flush = True)
    result1 = run_crew_0(system_user_message,verbose = True,datatools=[pandas_tool])

    print()
    print("---------------result1-------------")
    print(result1)
    print()

    return result1