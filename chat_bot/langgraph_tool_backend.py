from langgraph.graph import StateGraph, START
from typing import TypedDict, Annotated
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langgraph.graph.message import add_messages,BaseMessage
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

import requests
import random

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="NousResearch/Hermes-4-405B",
    task="text-generation",
)

model = ChatHuggingFace(llm=llm)


# Tools
# search tool
search_tool = DuckDuckGoSearchRun(region="us-en")

# Calculator tool
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    A simple calculator tool that can perform basic arithmetic operations.
    Args:
        first_num (float): The first number.
        second_num (float): The second number.
        operation (str): The operation to perform. Can be "add", "subtract", "multiply", or "divide".
    """
    if operation == "add":
        return {"result": first_num + second_num}
    elif operation == "subtract":
        return {"result": first_num - second_num}
    elif operation == "multiply":
        return {"result": first_num * second_num}
    elif operation == "divide":
        if second_num == 0:
            return {"error": "Cannot divide by zero"}
        return {"result": first_num / second_num}
    else:
        return {"error": "Invalid operation"}  

# stock price tool
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetches the current stock price for a given stock symbol using a public API.
    Args:         symbol (str): The stock symbol to fetch the price for.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=VZTFEFEKXZRBQI0G"
    r = requests.get(url)
    return r.json()


# Make tool List
tools = [get_stock_price, search_tool, calculator]

# Make the LLM tool aware
llm_with_tools =  model.bind_tools(tools=tools)



# State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# graph nodes
def chat_node(state: ChatState):
    """ LLM node that may answer or request a tool call"""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages':[response]}      


tool_node = ToolNode(tools)


graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)


graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile()
