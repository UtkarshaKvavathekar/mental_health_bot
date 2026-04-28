from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

chat_model = ChatOpenAI( model='openai/gpt-4.1',
    api_key= os.getenv("OPENAI_API_KEY"),
    base_url="https://models.github.ai/inference")

# responce = chat_model.invoke("hi")
# print(responce.content)

from langgraph.graph import StateGraph,MessagesState,START,END
from langgraph.graph.message import add_messages
from typing import Annotated,Literal,TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

def call_model(state:MessagesState):
    # Messagestate is predefined class-list of messgaes
    messages = state['messages']
    response = chat_model.invoke(messages)
    return {"messages":[response]}

workflow = StateGraph(MessagesState)
workflow.add_node('chatbot',call_model)
workflow.add_edge(START,"chatbot")
workflow.add_edge("chatbot",END)
app= workflow.compile()

input={"messages":[HumanMessage(content="HI,my name is Prad")]}

app.invoke(input)

@tool
def search(query:str):
    "This is my tool"
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "Its 60 degrees and frozen"
    return "Its 90 degree and sunny"

search.invoke("What is temp in sf?")
tools = [search]

tool_node = ToolNode(tools)
tool_node
