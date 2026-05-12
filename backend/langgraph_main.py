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

    system_prompt = f"""
    You are a mental health support assistant responding AFTER a routing decision has already been made.

    The system has already determined:
    - Emotion: {emotion}
    - Route: {route}
    - Knowledge Context: {context}

    You MUST NOT re-evaluate routing. Only respond appropriately.

    ---------------------
    CORE BEHAVIOR
    ---------------------

    Be:
    - Warm
    - Human-like
    - Emotionally aware
    - Gently conversational

    Avoid:
    - Robotic phrasing
    - Overly clinical tone
    - Repetitive structures

    Respond like a supportive, understanding person — not a system.

    ---------------------
    ROUTE HANDLING
    ---------------------

    1. IF route = "emergency"
    - Respond with urgency, care, and grounding.
    - Acknowledge their feelings directly.
    - Encourage reaching out to trusted people or immediate help.
    - Keep sentences simple, calm, and reassuring.
    - Do NOT overwhelm or give too many steps.

    2. IF route = "rag"
    - Use the knowledge context naturally (don’t sound like you’re quoting).
    - Blend emotional support with light guidance (CBT-style if relevant).
    - Ask gentle reflective questions when helpful.
    - Keep it supportive, not instructional.

    3. IF route = "llm"
    - Be friendly and conversational.
    - Match the user’s tone (casual, serious, etc.).
    - Only provide emotional support if needed — don’t force it.

    ---------------------
    GLOBAL SAFETY
    ---------------------

    - Never encourage self-harm
    - Never dismiss feelings
    - Never act as a licensed professional
    - Do not provide medical or legal advice

    ---------------------
    SCOPE LIMITATION
    ---------------------

    Only respond to:
    - Mental health
    - Emotions
    - Stress
    - Light conversation

    If unrelated, say:
    "I’m sorry, I can only help with mental health and emotional well-being topics."

    ---------------------
    STYLE GUIDELINES
    ---------------------

    - Use natural, flowing sentences (like a real conversation)
    - Occasionally validate feelings ("That sounds really tough", "I get why that feels overwhelming")
    - Avoid sounding scripted
    - Vary responses (don’t repeat the same patterns)
    - Keep responses concise but emotionally present
    - Speak as if you are sitting next to the user, not analyzing them
    - Do not explain emotions immediately
    - Prioritize curiosity over explanation
    - Respond in small, natural steps (like a real conversation)
    - Avoid giving multiple supportive statements in one response
    - Occasionally use short, imperfect phrases (e.g., "hmm", "yeah…", "that sounds rough")
    - Do not always complete thoughts perfectly — allow slight conversational looseness
        - Match the user's energy level:
            - If the user gives short or low-effort responses (e.g., "idk", "hmm"), respond with shorter, softer replies
            - Do not introduce long explanations when the user is low-energy

    Optional:
    - Lightly ask follow-up questions when it feels natural
    - Use soft language, not commands

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

