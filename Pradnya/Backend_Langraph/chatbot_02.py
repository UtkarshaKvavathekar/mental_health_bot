from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
from langgraph.graph import StateGraph,MessagesState,START,END
from langgraph.graph.message import add_messages
from typing import Annotated,Literal,TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from openai import BadRequestError



@tool
def Emergency_call():
    """
    Use this tool ONLY when the user expresses suicidal thoughts, self-harm intent,
    desire to die, or immediate danger to themselves.
    This tool must be called instead of providing therapy, reassurance, or advice.
    It should prioritize safety, crisis resources, and urgent real-world help.
    """
    print("calling")

class chatbot:
    def __init__(self):
        self.llm =  ChatOpenAI( model='openai/gpt-4.1',
                                api_key= os.getenv("GITHUB_TOKEN"),
                                base_url="https://models.github.ai/inference")

    def call_tool(self):
        tool = Emergency_call
        tools = [tool]
        self.tool_node = ToolNode(tools=tools)
        self.llm_with_tool = self.llm.bind_tools(tools)

    def call_model(self,state:MessagesState):
    # Messagestate is predefined class-list of messgaes
        messages = state['messages']
        response = self.llm_with_tool.invoke(messages)
        return {"messages":[response]}
      
    def router_function(self,state:MessagesState)->Literal["tools",END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def __call__(self):
        self.call_tool()
        
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent",self.call_model)
        workflow.add_node("tools",self.tool_node)

        workflow.add_edge(START,"agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools":"tools",END:END})
        workflow.add_edge("tools","agent")
        self.app = workflow.compile()
        return self.app

if __name__ == "__main__":
    mybot = chatbot()
    workflow = mybot()
    try:
        # Normal response
        response =  workflow.invoke({"messages":["it feels like life has no meaning now, lets end it"]})
        print(response['messages'][-1].content)
    except BadRequestError as e:
            error_text = str(e)

            if "content_filter" in error_text or "self_harm" in error_text:
                # 🔥 THIS IS THE IMPORTANT PART
                print("🚨 Bot: Don't give up this easily,hang in there.")
                print("🚨 Bot: You’re not alone. I’m calling emergency support now.")
                Emergency_call.invoke({})

                # Conversation CONTINUES
                print("\nBot: I’m still here with you.\n")
            else:
                # Unknown error → don’t hide bugs
                raise e



# __name__ is a special variable that Python sets automatically.
# If you run this file directly, Python sets:
# __name__ = "__main__"
# If this file is imported into another file, Python sets:
# __name__ = "filename"

# 🔹 Line 3
# workflow = mybot()
# This line is EXTREMELY IMPORTANT.
# Why does this even work?
# Because you defined:
# def __call__(self):
# That special name means:
# “This object can be called like a function.”
# So this line means:
# “Hey chatbot, build your workflow graph and give it to me.”
# Internally Python runs:
# workflow = mybot.__call__()
# And that:
# creates the StateGraph
# compiles it
# returns the runnable app
# So now:
# workflow = ready-to-run chatbot machine