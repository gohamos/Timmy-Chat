import os
import pandas as pd
from langchain.agents import Tool
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from crewai import Agent, Task, Crew



# Change the working directory to the current file's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"The current working directory is: {os.getcwd()}")

from load_llm import getLLM
from load_llm import getClient
from crews import run_crew_0
from load_data import loadfiles
from load_data import loadLookup
from load_data import mergingRecords
from load_data import printMeta
from load_data import convertRecordstoDocList

from helpers import get_completion_by_messages

##### NOTE This script assumes you have already run test_loadingofcsv.py to generate the "output" directory of preprocessed tables (replaces values in tables with lookup descriptions, removes invalid timestamps etc.) 

llm=getLLM()
client=getClient()
filterCols=["UP_POINT","DN_POINT","UP_LINK_ID","DN_LINK_ID","START_X_COOR","START_Y_COOR","END_X_COOR","END_Y_COOR","Q_END_X_COOR","Q_END_Y_COOR","TUNNEL_X","TUNNEL_Y"]




filelist = []
DictMap = dict()
EwayDict = dict()

ONLINE_DATA_TABLES=os.getenv('ONLINE_DATA_TABLES')
if len(ONLINE_DATA_TABLES)==0: 
    try:
        import streamlit as st
        ONLINE_DATA_TABLES= st.secrets['ONLINE_DATA_TABLES']
        print("[] Loaded secrets ONLINE_DATA_TABLES")
    except:
        print("[] Cannot find  ONLINE_DATA_TABLES")
        
else:    
    print("[] Loaded env ONLINE_DATA_TABLES")
DataList=[]
if len(ONLINE_DATA_TABLES)>0:
    DataList=ONLINE_DATA_TABLES.split(",")

print("[] Loading Data", flush=True)
if len(DataList)==0: 
    loadingorder=["outmerge_pkl","outpickle","output"]
    for path in loadingorder:
        filelist = loadfiles(dir=path,printdebug=0,subdir=0,reparse=0,filtercols=filterCols,filtertime=0,formattime=0)
        if len(filelist)>0:
           break;
else:
    filelist = loadfiles(filelist=DataList,printdebug=0,subdir=0,reparse=0,filtercols=filterCols,filtertime=0,formattime=0)   

ONLINE_LOOKUP_TABLES=os.getenv('ONLINE_LOOKUP_TABLES')
if len(ONLINE_LOOKUP_TABLES)==0: 
    try:
        import streamlit as st
        ONLINE_LOOKUP_TABLES= st.secrets['ONLINE_LOOKUP_TABLES']
        print("[] Loaded secrets ONLINE_LOOKUP_TABLES")
    except:
        print("[] Cannot find  ONLINE_LOOKUP_TABLES")
        
else:    
    print("[] Loaded env ONLINE_LOOKUP_TABLES")


print("[] Loading Lookup", flush=True)
LookupList=[]
if len(ONLINE_LOOKUP_TABLES)>0:
    LookupList=ONLINE_LOOKUP_TABLES.split(",")

if len(LookupList)>0:
    DictMap ,EwayDict =loadLookup(filelist=LookupList,printdebug=0,subdir=0)
else:
    for path in loadingorder:
       DictMap ,EwayDict =loadLookup(dir=path,printdebug=0,subdir=1)
       if len(DictMap)>0:
           break;
    

print(len(filelist))
#recordlist=mergingRecords(filelist,printdebug=1)
#print(len(recordlist))

from langchain.agents import Tool


toollist = []
histlist = []
exlist = []
for file in filelist:
    if "EXPRESSWAY" in file:
        exlist.append(filelist[file])
    else:
        histlist.append(filelist[file])
        
        
print("pandas_ir_agent:",len(histlist))
if len(histlist)>0:
    # Creating tool_agents (From 3rd party)
    pandas_ir_agent = create_pandas_dataframe_agent(
        llm=getLLM(),
        df = histlist, #list of panda dataframe
        agent_type=AgentType.OPENAI_FUNCTIONS,# <-- This is an "acknowledgement" that this can run potentially dangerous code
        allow_dangerous_code=True
    )

    # Create the tool
    pandas_ir_tool = Tool(
        name="Search and Analyze tabular Incident Record data with Code",
        func=pandas_ir_agent.invoke, # <-- This is the function that will be called when the tool is run. Note that there is no `()` at the end
        description="Useful for search-based queries for Incident Records.",
    )

    toollist.append(pandas_ir_tool)



   
    # Dictionary for the column description to support agent in understanding the dataframe if required to use.
# Important Note: The dictionary is not exhaustive and may have incorrect description but it is good enough to test if agent understand it. 
# To update dictionary again in the future.
columns_description = {
    "IR_ID": "Unique identifier for the Incident Record.",
    "TYPE": "Type of incident.",
    "START_TIME": "The time when the incident started, reported or observed.",
    "END_TIME": "The time when the incident was resolved. If empty, incident was NOT resolved!",
    "ROAD_NAME": "Name of the road where the incident occurred. Expressways are listed using their abbreviations",
    "UP_POINT": "Upstream reference point on the road near the incident location.",
    "DN_POINT": "Downstream reference point on the road near the incident location.",
    "UP_LINK_ID": "Unique identifier of the upstream road link (segment) near the incident.",
    "DN_LINK_ID": "Unique identifier of the downstream road link (segment) near the incident.",
    "START_X_COOR": "X-coordinate of the starting location of the incident.",
    "START_Y_COOR": "Y-coordinate of the starting location of the incident.",
    "END_X_COOR": "X-coordinate of the ending location of the incident.",
    "END_Y_COOR": "Y-coordinate of the ending location of the incident.",
    "LOC_TYPE": "Type of location where the incident occurred",
    "LOC_CODE": "Unique code associated with the incident location.",
    "LANE_BLOCKAGE": "Indicates whether lanes are blocked.",
    "CAM_ID": "Identifier of the camera monitoring the incident location.",
    "SOURCE": "Source of the incident report",
    "SOURCE_OTH": "Additional details or other sources for the incident report.",
    "DIR": "Direction of the traffic flow affected.",
    "CAUSE": "Root cause of the incident with the IR_ID. (Default = -1, if the incident is not caused by another incident).",
    "LOC_DETAIL": "Detailed description of the location",
    "UP_NODE_ID": "Unique identifier of the upstream node nearest to the incident.",
    "DN_NODE_ID": "Unique identifier of the downstream node nearest to the incident.",
    "UP_NODE_DESC": "Description of the upstream node location.",
    "DN_NODE_DESC": "Description of the downstream node location.",
    "DIST_TO_UPNODE": "Distance from the incident to the upstream node.",
    "CONGT_STATUS": "Status of congestion due to the incident. 1 means there is congestion, 0 otherwise",
    "CONGT_START_TIME": "The time when congestion started due to the incident.",
    "CONGT_END_TIME": "The time when congestion ended.",
    "Q_END_POINT": "The endpoint of the traffic queue caused by the incident expressed in km.",
    "Q_END_X_COOR": "X-coordinate of the queue endpoint.",
    "Q_END_Y_COOR": "Y-coordinate of the queue endpoint.",
    "TUNNEL_X": "X-coordinate of the tunnel (if incident occurred within a tunnel).",
    "TUNNEL_Y": "Y-coordinate of the tunnel (if incident occurred within a tunnel).",
    "VERI_STATE": "Verification state of the incident by the traffic operator.",
    "DISPATCH_VRS_TIME": "Time when Vehicle Recovery Service (VRS) was dispatched to handle the incident.",
    "DISPATCH_LTM_TIME": "Time when LTA Traffic Marshall (LTM) was dispatched.",
    "DISPLAY_IR_ID": "Display identifier for the Incident Record on Electronics Messages Signboard.",
    "NB_OF_VEH": "Number of vehicles involved in the incident.",
    "IMPORTANT": "Importance level of the incident.",
    "MAX_Q_LENGTH": "Maximum length of the traffic queue caused by the incident.",
    "CONGESTION_LENGTH": "Maximum length of the traffic congestion caused by the incident.",
    "TIME_OF_REMOVAL": "The time when the unattended vehicle was removed from the scene.",
    "DAMAGE": "Description of any visible damage to the vehicle.",
    "DANGER_TYPE": "The type of danger posed by the incident",
    "DANGER_TYPE_ID": "The type of danger posed by the incident",
    "DANGER_TYPE_OTH": "Other types of danger not covered under the standard DANGER_TYPE options.",
    "VALUABLE": "Indicates whether valuable items are present inside the unattended vehicle.",
    "CL_BY_TP": "Whether the incident was cleared or resolved by Traffic Police (TP).",
    "OTH": "Other details or observations related to the unattended vehicle incident.",
    "RD_WK_TYPE": "Type of road work being carried out.",
    "RD_WK_TYPE_DESC": "Detailed description of the specific road work activities.",
    "ACC_TYPE": "Type of accident.",
    "ACC_TYPE_OTH": "Other accident types not covered under 'ACC_TYPE'.",
    "ROAD_STATE": "Condition of the road at the time of the accident.",
    "FATAL_NO": "Number of fatalities resulting from the accident.",
    "SERIOUS_NO": "Number of serious injuries resulting from the accident.",
    "SLIGHT_NO": "Number of slight or minor injuries resulting from the accident.",
    "START_POINT": "Location where the congestion begins in KM mark.",
    "END_POINT": "Location where the congestion ends in KM mark.",
    "OBSTACLE_TYPE": "Type of obstacle detected that causes disruption to traffic.",
    "OBSTACLE_TYPE_OTH": "Details or description of the obstacle if 'Other' is selected for OBSTACLE_TYPE",
    "CUMU_CONGT": "Cumulative congestion caused by slow traffic",
}

for col in filterCols:
    if col in columns_description:
        del columns_description[col]
        
for col in columns_description:
    if col in DictMap:
        columns_description[col]=columns_description[col]+" Possible Values:"+",".join(DictMap[col].values())

columnstr = (str)(columns_description)
print(columnstr)

API_MODEL=os.getenv('OPENAI_MODEL_NAME')
def helper_cleanupquery(user_message, printdebug = 0):
    
    
    system_message = f"""
    When given a user message as input (delimited by \
    <incoming-massage> tags), check for spelling errors and grammatical mistakes and return a corrected query in proper English.
     
    Only if it is a query on a date, it will be in day-month-year format, that is to mean that 1/3/2022 is the 1st of March 2022, not the 3rd of January 2022.
    Check if it is a valid date in dd/mm/yyyy format. If not valid, then return "invalid date".
    Add "has a start date of <date>" to the query, replacing the original date in the query in a comprehensible and cohesive way
    If it has a range, include both dates from the first date 00:00 to the last date 23:59 unless otherwise stated.
    For example: How many incidents on 24/11/22? -> How many incidents have a start date of 24 November 2022?
    Another example: How many incidents from 24/11/22 - 26/11/22 -> How many incidents have a start date of 24 November 2022 00:00 to 26 November 2022 23:59?
    Another example: How many incidents in June 2024 -> How many incidents have a start date of 1 June 2024 00:00 to 30 June 2024 23:59?
    """

    system_message = f"""
    When given a user message as input (delimited by \
    <incoming-massage> tags), check for spelling errors and grammatical mistakes and return a corrected query in proper English.

    """
    messages =  [
        {'role':'system', 'content': system_message},
        {'role' : 'user', 'content': f"<incoming-massage> {user_message} </incoming-massage>"}
    ]
    
    #response = llm.invoke(messages)
    
    response = get_completion_by_messages(messages,client,model=API_MODEL )
    #if printdebug>0:
    #    print(response.usage_metadata)
    return response



def helper_checkrelevance(user_message,  printdebug = 0):
    system_message = f"""
    User is querying road traffic incident records from Singapore Land Transport Authority with data columns with descriptions delimited by the following json enclosed in <column> enclosed tags:
    <columns>{columns_description}</columns> 
    For the user query as input (delimited by <incoming-massage> tags), Check if the query is relevant to the data role, data set or road traffic related and return ONLY 'YES',\
    or if it is a general database or incident record query, then return ONLY 'DB', \
    otherwise return  'NO' and infer what is it related to """
    
    system_message = f"""
    User is querying road traffic incident records from Singapore Land Transport Authority.
    For the user query as input (delimited by <incoming-massage> tags), Check if the query is relevant to the data role, data set or road traffic related and return ONLY 'YES',\
    or if it is a general database or incident record query, then return ONLY 'DB', \
    otherwise return  'NO' and infer what is it related to """

    messages =  [
        {'role':'system', 'content': system_message},
        {'role' : 'user', 'content': f"<incoming-massage> {user_message} </incoming-massage>"}
    ]

    #response = llm.invoke(messages)
    response = get_completion_by_messages(messages,client,model=API_MODEL )
    #if printdebug>0:
    #    print(response.usage_metadata)
    return response

print()


def PrintResult(prompt, corrected,relevant,result):
    print()
    print("---------------Query-------------")
    print("-- Original    =",prompt)
    print("-- Corrected   =",corrected)
    print("-- Is Relevant?   =",relevant)
    print()
    print("---------------Result-------------")
    print(result)
    print()
    print("----------------------------------") 
    print(flush = True)


def databasesize():
    return len(toollist)
    
    
def response(prompt,printdebug=0):
    print()
    result1=""
    is_relevant=""
    clean_prompt=""
    if len(toollist)==0:
        result1="!!Sorry, no Data loaded in Database!"
    else:
        clean_prompt=helper_cleanupquery(prompt,printdebug=printdebug)
        is_relevant  =helper_checkrelevance(clean_prompt,printdebug=printdebug)
        if "NO" in is_relevant:
            result1="!!Please provide a query related to traffic incidents or road conditions in Singapore."
        else:            
            system_user_message = f"""You have access to a number of pandas dataframes. These pandas dataframes contain the traffic incident records from Land Transport Authority. \
            the datafranes uses columns with descriptions delimited by the following json enclosed in <column> enclosed tags:
            <columns>{columns_description}</columns>    

            All Date and Time based data queries and responses MUST be in Day/Month/Year hours:minutes format
            Use the DATE(START_TIME) as the reference point for Date and Time queries.

            Understand the question delimited by a pair of <text> enclosed and search the dataframes for relevant data within the provided context and give an accurate answer.
            Understand whether the question delimited by a pair of <text> enclosed is referring to all incidents or a specific type of incident. If it is a specific type of incident, please filter for that type of incident. Capitalize the first letter and leave the rest lowercase, example: "Apple", "Pear".
            Understand if the question delimited by a pair of <text> enclosed is referring to a particular road name and filter for that road name if it is required.
            Understand if the question delimited by a pair of <text> enclosed is referring to a particular time range and filter for the full time duration. (e.g. Days should filtered by 0:00 to 23:59 of that particular day, Months and Years should be 0:00 of the first day and 23:59 of the last day.)
            Use all the filters together using code if necessary.
            Don't assume you have access to any libraries other than built-in Python ones and pandas. \
            Make sure to refer only to the dataframes mentioned above. 

            Question: <text>{clean_prompt}</text>"""
            verbose=False
            if printdebug>0:
                verbose = True
                print("[] Calling crew",flush = True)
            result1 = run_crew_0(system_user_message,verbose=verbose,datatools=toollist,printdebug=printdebug,llm=llm)
    if printdebug>0:
        PrintResult(prompt,clean_prompt,is_relevant,result1)

    return result1, clean_prompt, is_relevant



if __name__ == "__main__":
    print("New Input>>>>>")    
    prompt = input ("Enter a query: ")
    while len(prompt)>0:
        result = response(prompt,printdebug=1)
        print("New Input>>>>>")
        prompt = input ("Enter a query: ")


