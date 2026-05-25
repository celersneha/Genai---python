import os
from typing import TypedDict, Annotated, List, Literal, Dict, Any
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langchain.messages import  AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="qwen/qwen3-32b")

class SupervisorState(MessagesState):
    """State for the supervisor multi-agent system"""
    next_agent: str = ""
    research_data: str = ""
    analysis: str = ""
    final_report: str = ""
    task_complete: bool = False
    current_task: str = ""
    
def create_supervisor_chain():
    """Created the supervisor decision chain"""
    
    supervisor_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
    You are a supervisor managing a team of agents:

    1. Researcher - Gathers information and data
    2. Analyst - Analyzes data and provides insights
    3. Writer - Creates reports and summaries

    Based on the current state and conversation, decide which agent should work next.
    If the task is complete, respond with 'DONE'.

    Current state:
    - Has research data: {has_research}
    - Has analysis: {has_analysis}
    - Has report: {has_report}

    Respond with ONLY the agent name (researcher/analyst/writer) or 'DONE'.
    """
        ),
        ("human", "{task}")
    ])

    return supervisor_prompt | llm

def supervisor_agent(state: SupervisorState) -> Dict:
    """Supervisor decides next agent using GROQ LLM"""
    
    messages = state["messages"]
    task = messages[-1].content if messages else "No task"
    
    # Check what's been completed
    has_research = bool(state.get("research_data",""))
    has_analysis = bool(state.get("analysis",""))
    has_report = bool(state.get("final_report" , ""))
    
    # Chain llm decision
    chain = create_supervisor_chain()
    decision = chain.invoke({
        "task" : task,
        "has_research":has_research,
        "has_analysis": has_analysis,
        "has_report": has_report
    })
    
    # Parse decision
    decision_text = decision.content.strip().lower()
    
    # Determine next agent
    if "done" in decision_text or has_report:
        next_agent= "end"
        supervisor_msg="✅Supervisor: All tasks complete!!"
    elif "researcher" in decision_text or not has_research:
        next_agent = "researcher"
        supervisor_msg = "📃Supervisor: Let's start with research"
    elif "analyst" in decision_text or (has_research and not has_analysis):
        next_agent= "analyst"
        supervisor_msg = "📃Supervisor: Research Done!! Let's start with analysis"
    elif "writer" in decision_text or (has_analysis and not has_report):
        next_agent= "writer"
        supervisor_msg = "📃Supervisor: Analysis Done!! Let's create the report"
    else:
        next_agent="end"
        supervisor_msg="✅Task seems complete"
    
    return {
        "messages" : [AIMessage(content=supervisor_msg)],
        "next_agent" : next_agent,
        "current_task" : task
    }
    
# Research Agent
def researcher_agent(state: SupervisorState) -> Dict:
    """Researcher agent used groq llm to gather information"""
    
    task = state.get("current_task" , "research_topic")
    
    # Create research prompt
    research_prompt = f"""
    As a research specialist, provide comprehensive information about: {task}

    Include:
    1. Key facts and background
    2. Current trends or developments
    3. Important statistics or data points
    4. Notable examples or case studies

    Be concise but thorough.
    """
    
    research_response = llm.invoke([HumanMessage(content=research_prompt)])
    research_data = research_response.content
    
    # create agent message
    agent_message = f"🔍Researcher: I have completed my research on '{task}'.\n\nKey findings: \n{research_data}"
    
    return {
        "messages" : [AIMessage(content=agent_message)],
        "next_agent" : "supervisor",
        "research_data": research_data
    }
    
# Analyst agent
def analysis_agent(state: SupervisorState) -> Dict:
    """Analyst agent uses groq to analyze the research"""
    research_data = state.get("research_data")
    task = state.get("current_task")
    
    # Create analysis prompt
    analysis_prompt = f"""
    As a data analyst, analyze this research data and provide insights:

    Research Data:
    {research_data}

    Provide:
    1. Key insights and patterns
    2. Strategic implications
    3. Risks and opportunities
    4. Recommendations

    Focus on actionable insights related to: {task}
    """
    
    # get analysis from llm
    analysis_response = llm.invoke([HumanMessage(content=analysis_prompt)])
    analysis = analysis_response.content
    
    agent_message = f"📊Analyst: I've completed the analysis.\n\nTop insights:\n{analysis[:400]}..."
    
    return {
        "messages": [AIMessage(content=agent_message)],
        "analysis": analysis,
        "next_agent":"supervisor"
    }

# writer agent
def writer_agent(state: SupervisorState) -> Dict:
    """Writer uses groq llm to create final report"""
    
    research_data = state.get("research_data","")
    analysis = state.get("analysis","")
    task = state.get("current_task" , "")
    
    # Create writing prompt
    writing_prompt = f"""
    As a professional writer, create an executive report based on:

    Task: {task}

    Research Findings:
    {research_data[:1000]}

    Analysis:
    {analysis[:1000]}

    Create a well-structured report with:
    1. Executive Summary
    2. Key Findings
    3. Analysis & Insights
    4. Recommendations
    5. Conclusion

    Keep it professional and concise.
    """
    report_response = llm.invoke([HumanMessage(content = writing_prompt)])
    report = report_response.content
    
    # Create final formatted report
    final_report = f"""
    FINAL REPORT
    {'-' * 50}

    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    Topic: {task}

    {'-' * 50}

    {report}

    {'-' * 50}

    Report compiled by Multi-Agent AI System powered by Groq
    """
    
    return {
        "messages":[AIMessage(content=f"✍️Writer: Report complete!! See below for full document")],
        "final_report":final_report,
        "next_agent":"supervisor",
        "task_complete":True
    }
    
# router function
def router(state: SupervisorState) -> Literal["supervisor", "researcher", "analyst" , "writer", "__end__"]:
    next_agent = state.get("next_agent","supervisor")
    
    if next_agent == "end" or state.get("task_complete", False):
        return END
    
    if next_agent in ["supervisor", "researcher", "analyst", "writer"]:
        return next_agent
    
    return "supervisor"

# Create workflow
workflow = StateGraph(SupervisorState)

# add nodes
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("analyst", analysis_agent)
workflow.add_node("writer", writer_agent)

# set entry point
workflow.set_entry_point("supervisor")

# add routing
for node in ["supervisor", "researcher", "analyst" , "writer"]:
    workflow.add_conditional_edges(
        node, 
        router,
        {
            "supervisor": "supervisor",
            "researcher":"researcher",
            "analyst":"analyst",
            "writer":"writer",
            END:END
        }
    )

graph = workflow.compile()

## view
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# # for saving the graph image
# png_data = graph.get_graph().draw_mermaid_png()

# with open("graph.png", "wb") as f:
#     f.write(png_data)

# print("Graph image saved!")

res = graph.invoke({
    "messages": [
        HumanMessage(
            content="What are the benefits and risks of AI in healthcare?"
        )
    ]
})

print(res)