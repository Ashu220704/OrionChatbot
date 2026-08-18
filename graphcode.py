from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition

from tools import(
    internet_search,
    latest_news,
    weather,
    currency_converter
)

tools=[
        internet_search,
        latest_news,
        weather,
        currency_converter
]

load_dotenv()

# -----------------------------------------
# LLM
# -----------------------------------------

llm = ChatOpenAI(
    model="gpt-5.4-mini",
).bind_tools(tools)

# -----------------------------------------
# State
# -----------------------------------------

class ChatState(TypedDict):

    messages: Annotated[list, add_messages]

# -----------------------------------------
# Node
# -----------------------------------------

def chatbot(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }

# -----------------------------------------
# Checkpointing mechanism persistency
# -----------------------------------------
connection=sqlite3.connect(database="AI_chatbot.db",check_same_thread=False)
sqlcheckpointer = SqliteSaver(conn=connection)

# -----------------------------------------
# Graph
# -----------------------------------------
tool_node=ToolNode(tools)

builder = StateGraph(ChatState)

builder.add_node("chatbot", chatbot)
builder.add_node("tools",tool_node)

builder.add_edge(START, "chatbot")
builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
builder.add_edge("tools","chatbot")

graph = builder.compile(checkpointer=sqlcheckpointer)