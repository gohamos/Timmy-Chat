
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv



def run_crew_0(topic,verbose=True, memory=False,printdebug=1, datatools=[], llm=None):
    
    if llm is not None:
        print("Use arg LLM")
        agent_data_analyst = Agent(
            llm = llm,
            role="data_analyst",
            goal="""Analyze the data based on user query: {topic}""",
            backstory=f"""You're the best data analyst. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
            You are very accurate and take into account all the nuances in data.""",
            allow_delegation=True,
            verbose=verbose,
            tools=datatools, #<--- This is the line that includes the tool
            max_iter=10,  # Increase the iteration limit
            max_execution_time=None
        )
    else:
        print("Use internal LLM")
        agent_data_analyst = Agent(
            role="data_analyst",
            goal="""Analyze the data based on user query: {topic}""",
            backstory=f"""You're the best data analyst. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
            You are very accurate and take into account all the nuances in data.""",
            allow_delegation=True,
            verbose=verbose,
            tools=datatools, #<--- This is the line that includes the tool
            max_iter=10,  # Increase the iteration limit
            max_execution_time=None
        )
   


    # Creating Tasks
    task_analyze = Task(
        description="""\
            1. Understand the user query: {topic}.
            2. Breakdown the query into subtasks
            3. Use the tool to search the data based on the user query.
            4. Derive additional data where required.
            5. Analyse significant insights, trends, patterns if required.""",

        expected_output="""\
        Present the results with relevant data based on the user query""",

        agent=agent_data_analyst,
    )

   

    # Creating the Crew
    crew = Crew(
        agents=[ agent_data_analyst],
        tasks=[ task_analyze],
        verbose=verbose,
        memory=memory,
        
    )

    # Running the Crew
    result = crew.kickoff(inputs={"topic": f"""{topic}"""})
    if printdebug==1:
        print(f"Raw Output: {result.raw}")
        print("-----------------------------------------\n\n")
        print(f"Token Usage: {result.token_usage}")
        print("-----------------------------------------\n\n")
        print(f"Tasks Output of Task 1: {result.tasks_output[0]}")
        print("-----------------------------------------\n\n")
        
    elif printdebug>1:
        print("-----------------------------------------\n\n")
        print(f"Results: {result}")
        print("-----------------------------------------\n\n")

    return result.raw
    

def run_crew_0b(topic,verbose=True, memory=False,printdebug=0, datatools=[], llm=None):
    
    
    if llm is not None:
    
        agent_data_analyst = Agent(
            llm = llm,
            role="data_analyst",
            goal="""Analyze the data based on user query: {topic}""",
            backstory=f"""You're the best data analyst. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
            You are very accurate and take into account all the nuances in data.""",
            allow_delegation=True,
            verbose=True,
            tools=datatools, #<--- This is the line that includes the tool
            max_iter=30,  # Increase the iteration limit
        )
    else:
        agent_data_analyst = Agent(
            role="data_analyst",
            goal="""Analyze the data based on user query: {topic}""",
            backstory=f"""You're the best data analyst. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
            You are very accurate and take into account all the nuances in data.""",
            allow_delegation=True,
            verbose=True,
            tools=datatools, #<--- This is the line that includes the tool
            max_iter=30,  # Increase the iteration limit
        )
   
    
   


    # Creating Tasks
    task_analyze = Task(
        description="""\
            1. Understand the user query: {topic}.
            2. Breakdown the query into subtasks
            3. Use the tool to search the data based on the user query.
            4. Derive additional data where required.
            5. Analyse significant insights, trends, patterns if required.""",

        expected_output="""\
        Present, step by step, the results with relevant data based on the user query""",

        agent=agent_data_analyst,
    )

   

    # Creating the Crew
    crew = Crew(
        agents=[ agent_data_analyst],
        tasks=[ task_analyze],
        verbose=verbose,
        memory=memory
    )

    # Running the Crew
    result = crew.kickoff(inputs={"topic": f"""{topic}"""})
    if printdebug>0:
        print(f"Raw Output: {result.raw}")
        print("-----------------------------------------\n\n")
        print(f"Token Usage: {result.token_usage}")
        print("-----------------------------------------\n\n")
        print(f"Tasks Output of Task 1: {result.tasks_output[0]}")
        print("-----------------------------------------\n\n")

    return result.raw
    
    
def run_crew_1(topic,verbose=True, memory=False, datatools=[], llm=None):


    # Creating Agents
    if llm is not None:
    
        agent_database_specialist = Agent(
            llm = llm,
            role="database_specialist",
            goal=f"""Search the data based on user query: {topic}""",
            backstory="""You're the best database specialist. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
            You are very accurate and take into account all the nuances in data. You do not require human input to validate your result""",
            allow_delegation=False,
            verbose=False,
            tools=datatools, #<--- This is the line that includes the tool
        )
    else:
        agent_database_specialist = Agent(
            role="database_specialist",
            goal=f"""Search the data based on user query: {topic}""",
            backstory="""You're the best database specialist. You specializes in organizing data for quick retrieval and analysis from traffic incident data. 
            You are very accurate and take into account all the nuances in data. You do not require human input to validate your result""",
            allow_delegation=False,
            verbose=False,
            tools=datatools, #<--- This is the line that includes the tool
        )


    # Creating Tasks
    task_search = Task(
        description=f"""\
            1. Understand the user query based on the topic: {topic}. 
            2. Use the tool to search and retrieve the data to answer the user query. 
            """,

        expected_output="""\
        Accurate search and analysis result in markdown format""",

        agent=agent_database_specialist,
        human_input = True
    )

    # Creating the Crew
    crew = Crew(
        agents=[agent_database_specialist],
        tasks=[task_search],
        verbose=verbose,
        memory=False
    )

    # Running the Crew
    result = crew.kickoff(inputs={"topic": f"{topic}"})

    

    if printdebug>0:
        print(f"Raw Output: {result.raw}")
        print("-----------------------------------------\n\n")
        print(f"Token Usage: {result.token_usage}")
        print("-----------------------------------------\n\n")
        print(f"Tasks Output of Task 1: {result.tasks_output[0]}")
        print("-----------------------------------------\n\n")

    return result.raw