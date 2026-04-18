from typing import TypedDict,List
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage,SystemMessage
from langgraph.graph import StateGraph,START,END,MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

sqlite_conn=sqlite3.connect("checkpoint.sqlite",check_same_thread=False)
memory=SqliteSaver(sqlite_conn)

#My moduls
from emotion_node import emotion_node
from rag import retrieve_context

#Define State
class ChatState(TypedDict):
    messages:List[BaseMessage]
    emotion:str
    context:str
    route:str


# if __name__=="__main__":
#     test_state={
#         "messages":[HumanMessage(content="I feel very anxious today")]
#     }
#     print(emotion_node(test_state))

#Emergency function:
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, EMERGENCY_CONTACT
from twilio.rest import Client

def emergency_call():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to = EMERGENCY_CONTACT,
        from_ =TWILIO_FROM_NUMBER,
        url = "http://demo.twilio.com/docs/voice.xml"
    )

    return {
        "status": "called",
        "call_sid": call.sid
    }

def router_node(state:ChatState):
    emotion=state.get("emotion","").lower()
    user_msg=state["messages"][-1].content.lower()

    #Safety check
    if any(word in  user_msg for word in["kill myself",
        "end my life",
        "suicide",
        "want to die",
        "no reason to live",
        "better off dead",
        "hurt myself",
        "end it all",
        "die"]):
        return{"route":"emergency"}
    
    #Emotion based
    if emotion in["suicidal","severe_distress"]:
        return{"route":"emergency"}
    
    #RAG
    if emotion in ["sad","anxious","stressed","depressed","angry"]:
        if len(user_msg.split()) > 4:
            return {"route": "rag"}
    
    #Normal convo
    return{"route":"llm"}

# if __name__ == "__main__":
#     test_state = {
#         "messages": [HumanMessage(content="I feel very anxious these days")],
#         "emotion": "anxious"
#     }

#     print(router_node(test_state))

#Rag node
def rag_node(State:ChatState):
    user_msg=State["messages"][-1].content

    context=retrieve_context(user_msg)
    return{
        "context":context
    }

# if __name__ == "__main__":
#     test_state = {
#         "messages": [HumanMessage(content="How to deal with anxiety?")]
#     }

#     print(rag_node(test_state))

#Emergency node:
def emergency_node(state: dict):
    print("🚨 Emergency triggered")

    result = emergency_call()

    return {
        **state,
        "emergency": result
    }


#Building the agent

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv("../../.env")

llm = ChatOpenAI(
    model="openai/gpt-4.1",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference"
)
# response = llm.invoke("hi")
# print(response.content)

def call_model(State:ChatState):
    messages=State["messages"]
    emotion=State.get("emotion","neutral")
    context=State.get("context", "")
    route=State.get("route","")

    system_prompt=f"""
    You are a mental health assistant that responds ONLY after a routing decision has already been made.

The system has already classified the user’s situation using:
- Emotion detection
- Safety routing
- Context retrieval (RAG if needed)

Your job is NOT to decide routing.
Your job is ONLY to respond appropriately based on the provided context.

---------------------
INPUT CONTEXT
---------------------
Emotion: {emotion}
Route: {route}
Knowledge Context: {context}

---------------------
BEHAVIOR RULES
---------------------

1. IF route = "emergency"
- Respond with urgency, care, and support.
- Encourage the user to seek immediate help.
- Do NOT mention tools or systems.
- Do NOT try to solve everything.
- Keep it calm, grounding, and supportive.

2. IF route = "rag"
- Use the provided knowledge context to guide your response.
- Provide supportive, CBT-style or structured guidance.
- Be empathetic but slightly more informative.

3. IF route = "llm"
- Respond normally in a friendly, conversational way.
- No therapy unless emotion clearly indicates distress.

---------------------
GLOBAL SAFETY RULES
---------------------

- Never encourage self-harm.
- Never dismiss emotional pain.
- Never act like a human therapist with authority.
- Do not provide medical or legal advice.
- Be supportive, not overwhelming.

---------------------
SCOPE LIMITATION
---------------------

You must ONLY respond to:
- Mental health
- Emotional wellbeing
- Stress-related conversations
- Light general conversation

If the user asks something unrelated, respond with:
"I’m sorry, I can only help with mental health and emotional well-being topics."

---------------------
STYLE
---------------------

- Calm
- Human-like
- Supportive
- Not too long
- Not robotic



    """
    final_messages = [SystemMessage(content=system_prompt)] + messages
    response=llm.invoke(final_messages)
    return{
        "messages":[response]
    }


def route_decision(state:ChatState):
    return state["route"]

#Building graph
#1.Create workflow
workflow=StateGraph(MessagesState)

#2.Add nodes
workflow.add_node("emotion",emotion_node)
workflow.add_node("router",router_node)
workflow.add_node("rag",rag_node)
workflow.add_node("agent",call_model)
workflow.add_node("emergency",emergency_node)

#3.Define flow
workflow.add_edge(START,"emotion")
workflow.add_edge("emotion","router")

#4.Addind conditional routing
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag": "rag",
        "llm": "agent",
        "emergency": "emergency"   # temporary (until you add emergency node)
    }
)

#5.Connect rag to agent

workflow.add_edge("rag","agent")

#6.Define the end
workflow.add_edge("agent",END)

#7.Compile the app
app=workflow.compile(checkpointer=memory)
config={"configurable":{
    "thread_id":1
}}

from langchain_core.messages import HumanMessage

