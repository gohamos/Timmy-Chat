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

load_dotenv('.env')

# load IR tabular data into panda dataframe
df_ir_accident = pd.read_csv("HIST_IR info since 2022/HIST_IR_ACC.csv")
df_ir_breakdown = pd.read_csv("HIST_IR info since 2022/HIST_IR_BREAKDOWN.csv")
df_ir_congestion = pd.read_csv("HIST_IR info since 2022/HIST_IR_CONGESTION_LEN.csv")
df_ir_obstacle = pd.read_csv("HIST_IR info since 2022/HIST_IR_OBSTACLE.csv")
df_ir_plant_failure = pd.read_csv("HIST_IR info since 2022/HIST_IR_PLANT_FAILURE.csv")
df_ir_roadwork = pd.read_csv("HIST_IR info since 2022/HIST_IR_rdwk.csv")
df_ir_slow_traffic = pd.read_csv("HIST_IR info since 2022/HIST_IR_SLOWTRAF.csv")
df_ir_unattend_vehicle = pd.read_csv("HIST_IR info since 2022/HIST_IR_UNATTEND_VEH.csv")
df_ir_weather = pd.read_csv("HIST_IR info since 2022/HIST_IR_WEATHER.csv")
df_ir = pd.read_csv("HIST_IR info since 2022/HIST_IR.csv")
lst_df_ir = [df_ir_accident, df_ir_breakdown, df_ir_congestion, df_ir_obstacle, df_ir_plant_failure, df_ir_roadwork, df_ir_slow_traffic, df_ir_unattend_vehicle, df_ir_weather, df_ir]

# load lookup tabular data into panda dataframe
df_lookup_gis_cooridor = pd.read_csv("Lookup Table/gis_corridor.csv")
df_lookup_gis_expressway = pd.read_csv("Lookup Table/gis_expressway_1.csv")
df_lookup_ir_accident = pd.read_csv("Lookup Table/ir_accident.csv")
df_lookup_breakdown = pd.read_csv("Lookup Table/ir_breakdown_type.csv")
df_lookup_danger = pd.read_csv("Lookup Table/ir_danger_type.csv")
df_lookup_ir_dir = pd.read_csv("Lookup Table/IR_DIR.csv")
df_lookup_loc_code = pd.read_csv("Lookup Table/IR_loc_code.csv")
df_lookup_loc_type = pd.read_csv("Lookup Table/IR_loc_type.csv")
df_lookup_obstacle = pd.read_csv("Lookup Table/ir_obstacle_type.csv")
df_lookup_opinion = pd.read_csv("Lookup Table/ir_opinion.csv")
df_lookup_rdwk_type = pd.read_csv("Lookup Table/ir_rdwk_type.csv")
df_lookup_road_state = pd.read_csv("Lookup Table/ir_road_state.csv")
df_lookup_traffic_state = pd.read_csv("Lookup Table/ir_traffic_state.csv")
df_lookup_ir_type = pd.read_csv("Lookup Table/ir_rdwk_type.csv")
df_lookup_veri_state = pd.read_csv("Lookup Table/IR_veri_state.csv")
df_lookup_visibility = pd.read_csv("Lookup Table/ir_visibility.csv")
df_lookup_weather_detail = pd.read_csv("Lookup Table/ir_weather_detail.csv")
df_lookup_weather_event = pd.read_csv("Lookup Table/ir_weather_event.csv")
lst_df_lookup = [df_lookup_gis_cooridor, df_lookup_gis_expressway, df_lookup_ir_accident, 
                 df_lookup_breakdown, df_lookup_danger, df_lookup_ir_dir, df_lookup_loc_code,
                 df_lookup_loc_type, df_lookup_obstacle, df_lookup_opinion, df_lookup_rdwk_type,
                 df_lookup_road_state, df_lookup_traffic_state, df_lookup_ir_type, df_lookup_veri_state,
                 df_lookup_visibility, df_lookup_weather_detail, df_lookup_weather_event]

# Create the df_context for system_prompt
df_template = """\`\`\`python
{df_name}.head().to_markdown()
>>> {df_head}
\`\`\`"""
df_context = "\n\n".join(
    df_template.format(df_head=_df.head().to_markdown(), df_name=df_name)
    for _df, df_name in [(df_ir, "df_1"), (df_ir_accident, "df_2"), (df_ir_breakdown, "df_3"), (df_ir_congestion, "df_4"),
                          (df_ir_obstacle, "df_5"), (df_ir_plant_failure, "df_6"), (df_ir_roadwork, "df_7"), (df_ir_slow_traffic, "df_8"),
                          (df_ir_unattend_vehicle, "df_9"), (df_ir_weather, "df_10"), (df_lookup_gis_cooridor, "df_11"), (df_lookup_gis_expressway, "df_12"),
                          (df_lookup_ir_accident, "df_13"),(df_lookup_breakdown, "df_14"),(df_lookup_danger, "df_15"), (df_lookup_ir_dir, "df_16"),
                          (df_lookup_loc_code, "df_17"),(df_lookup_loc_type, "df_18"),(df_lookup_obstacle, "df_19"),(df_lookup_opinion, "df_20"),
                          (df_lookup_rdwk_type, "df_21"),(df_lookup_road_state, "df_22"),(df_lookup_traffic_state, "df_23"),(df_lookup_ir_type, "df_24"),
                          (df_lookup_veri_state, "df_25"),(df_lookup_visibility, "df_26"),(df_lookup_weather_detail, "df_27"),(df_lookup_weather_event, "df_28"),]
)

# Dictionary for the column description to support agent in understanding the dataframe if required to use.
# Important Note: The dictionary is not exhaustive and may have incorrect description but it is good enough to test if agent understand it. 
# To update dictionary again in the future.
columns_description = {
    "IR_ID": "Unique identifier for the Incident Record.",
    "TYPE": "Type of incident (e.g., accident, roadblock, etc.).",
    "START_TIME": "The time when the incident started, reported or observed.",
    "END_TIME": "The time when the incident was resolved.",
    "ROAD_NAME": "Name of the road where the incident occurred.",
    "UP_POINT": "Upstream reference point on the road near the incident location.",
    "DN_POINT": "Downstream reference point on the road near the incident location.",
    "UP_LINK_ID": "Unique identifier of the upstream road link (segment) near the incident.",
    "DN_LINK_ID": "Unique identifier of the downstream road link (segment) near the incident.",
    "START_X_COOR": "X-coordinate of the starting location of the incident.",
    "START_Y_COOR": "Y-coordinate of the starting location of the incident.",
    "END_X_COOR": "X-coordinate of the ending location of the incident.",
    "END_Y_COOR": "Y-coordinate of the ending location of the incident.",
    "LOC_TYPE": "Type of location where the incident occurred (e.g., Expressway, tunnel, arterial road, etc.).",
    "LOC_CODE": "Unique code associated with the incident location.",
    "LANE_BLOCKAGE": "Indicates whether lanes are blocked (e.g., number of blocked lanes).",
    "CAM_ID": "Identifier of the camera monitoring the incident location.",
    "SOURCE": "Source of the incident report (e.g., police, public, sensors, etc.).",
    "SOURCE_OTH": "Additional details or other sources for the incident report.",
    "DIR": "Direction of the traffic flow affected.",
    "CAUSE": "Root cause of the incident with the IR_ID. (Default = -1, if the incident is not caused by another incident).",
    "LOC_DETAIL": "Detailed description of the location (e.g., proximity to landmarks).",
    "UP_NODE_ID": "Unique identifier of the upstream node nearest to the incident.",
    "DN_NODE_ID": "Unique identifier of the downstream node nearest to the incident.",
    "UP_NODE_DESC": "Description of the upstream node location.",
    "DN_NODE_DESC": "Description of the downstream node location.",
    "DIST_TO_UPNODE": "Distance from the incident to the upstream node.",
    "CONGT_STATUS": "Status of congestion due to the incident.",
    "CONGT_START_TIME": "The time when congestion started due to the incident.",
    "CONGT_END_TIME": "The time when congestion ended.",
    "Q_END_POINT": "The endpoint of the traffic queue caused by the incident expressed in km.",
    "Q_END_X_COOR": "X-coordinate of the queue endpoint.",
    "Q_END_Y_COOR": "Y-coordinate of the queue endpoint.",
    "TUNNEL_X": "X-coordinate of the tunnel (if incident occurred within a tunnel).",
    "TUNNEL_Y": "Y-coordinate of the tunnel (if incident occurred within a tunnel).",
    "VERI_STATE": "Verification state of the incident by the traffic operator (e.g., confirmed, unverified).",
    "DISPATCH_VRS_TIME": "Time when Vehicle Recovery Service (VRS) was dispatched to handle the incident.",
    "DISPATCH_LTM_TIME": "Time when LTA Traffic Marshall (LTM) was dispatched.",
    "DISPLAY_IR_ID": "Display identifier for the Incident Record on Electronics Messages Signboard.",
    "NB_OF_VEH": "Number of vehicles involved in the incident.",
    "IMPORTANT": "Importance level of the incident (e.g., high-priority incident).",
    "MAX_Q_LENGTH": "Maximum length of the traffic queue caused by the incident.",
    "TIME_OF_REMOVAL": "The time when the unattended vehicle was removed from the scene.",
    "DAMAGE": "Description of any visible damage to the vehicle (e.g., broken windows, dents).",
    "DANGER_TYPE": "The type of danger posed by the incident",
    "DANGER_TYPE_ID": "The type of danger posed by the incident",
    "DANGER_TYPE_OTH": "Other types of danger not covered under the standard DANGER_TYPE options.",
    "VALUABLE": "Indicates whether valuable items are present inside the unattended vehicle.",
    "CL_BY_TP": "Whether the incident was cleared or resolved by Traffic Police (TP).",
    "OTH": "Other details or observations related to the unattended vehicle incident.",
    "RD_WK_TYPE": "Type of road work being carried out (e.g., construction, maintenance, resurfacing).",
    "RD_WK_TYPE_DESC": "Detailed description of the specific road work activities.",
    "ACC_TYPE": "Type of accident (e.g., collision, rollover, hit-and-run).",
    "ACC_TYPE_OTH": "Other accident types not covered under 'ACC_TYPE'.",
    "ROAD_STATE": "Condition of the road at the time of the accident (e.g., wet, dry, icy).",
    "FATAL_NO": "Number of fatalities resulting from the accident.",
    "SERIOUS_NO": "Number of serious injuries resulting from the accident.",
    "SLIGHT_NO": "Number of slight or minor injuries resulting from the accident.",
    "START_POINT": "Location where the congestion begins in KM mark.",
    "END_POINT": "Location where the congestion ends in KM mark.",
    "OBSTACLE_TYPE": "Type of obstacle detected that causes disruption to traffic (e.g., vehicle breakdown, debris, etc.)",
    "OBSTACLE_TYPE_OTH": "Details or description of the obstacle if 'Other' is selected for OBSTACLE_TYPE",
    "CUMU_CONGT": "Cumulative congestion caused by slow traffic",
}

# Creating tool_agents (From 3rd party)
pandas_tool_lookup_agent = create_pandas_dataframe_agent(
    llm=ChatOpenAI(temperature=0, model='gpt-4o-mini'),
    df = lst_df_lookup, #list of panda dataframe
    agent_type=AgentType.OPENAI_FUNCTIONS,# <-- This is an "acknowledgement" that this can run potentially dangerous code
    allow_dangerous_code=True
)

pandas_tool_ir_agent = create_pandas_dataframe_agent(
    llm=ChatOpenAI(temperature=0, model='gpt-4o-mini'),
    df = lst_df_ir + lst_df_lookup, #list of panda dataframe
    agent_type=AgentType.OPENAI_FUNCTIONS,# <-- This is an "acknowledgement" that this can run potentially dangerous code
    allow_dangerous_code=True
)

# Create the tool
pandas_lookup_tool = Tool(
    name="Search lookup tabular data with Code",
    func=pandas_tool_lookup_agent.invoke, # <-- This is the function that will be called when the tool is run. Note that there is no `()` at the end
    description="Useful for search-based queries",
)

pandas_ir_tool = Tool(
    name="Search and Analyze tabular data with Code",
    func=pandas_tool_ir_agent.invoke, # <-- This is the function that will be called when the tool is run. Note that there is no `()` at the end
    description="Useful for search-based queries",
)

system_user_messages = []

def process_user_message(topic):
    # Create System_Prompt
    system_user_message = f"""You have access to a number of pandas dataframes. These pandas dataframes contain the traffic incident records from Land Transport Authority. \
        df_1 = All traffic incident records.
        df_2 = Accident incident records
        df_3 = Breakdown incident records
        df_4 = Congestion incident records
        df_5 = Obstacle incident records
        df_6 = Plant failure incident records
        df_7 = Road work incident records
        df_8 = Slow traffic incident records
        df_9 = Unattended vehicle incident records
        df_10 = Weather incident records
        df_11 to df_28 provide the lookup table of the data attribute for df_1 to df_10.
        Here is a sample of rows from each dataframe and the python code that was used to generate the sample:
        {df_context}
        
        Understand the question delimited by a pair of <text> enclosed and search the dataframes for relevant data within the provided context and give an accurate answer.
        Don't assume you have access to any libraries other than built-in Python ones and pandas. \
        Make sure to refer only to the dataframes mentioned above.
        
        Question: <text>{topic}</text>
        """
     
    # Creating Agents
    agent_database_specialist = Agent(
       role="database_specialist",
       goal="Search the data based on user query: {topic}",
       backstory="""You're the best database specialist. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
       You are very accurate and take into account all the nuances in data.""",
       allow_delegation=False,
       verbose=True,
       tools=[pandas_ir_tool], #<--- This is the line that includes the tool
       )


    # Creating Tasks
    task_search = Task(
        description="""\
            1. Understand the user query based on the topic: {topic}. 
            2. Use the tool to search and retrieve the data to answer the user query. 
            """,

        expected_output="""\
        Accurate search and analysis result in markdown format""",

        agent=agent_database_specialist,
        human_input = False
    )

    # Creating the Crew
    crew = Crew(
        agents=[agent_database_specialist],
        tasks=[task_search],
        verbose=True
    )

    # Running the Crew
    result = crew.kickoff(inputs={"topic": "{system_user_messages}"})

    print(result)

    #print(f"Raw Output: {result.raw}")
    #print("-----------------------------------------\n\n")
    #print(f"Token Usage: {result.token_usage}")
    #print("-----------------------------------------\n\n")
    #print(f"Tasks Output of Task 1: {result.tasks_output[0]}")
    #print("-----------------------------------------\n\n")
    #print(f"Tasks Output of Task 2: {result.tasks_output[1]}")

    return result