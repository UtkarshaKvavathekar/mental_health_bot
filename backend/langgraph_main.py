from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

sqlite_conn = sqlite3.connect("checkpoint.sqlite", check_same_thread=False)
memory = SqliteSaver(sqlite_conn)

# My modules
from emotion_node import emotion_node
from rag import retrieve_context


# Define State
class ChatState(TypedDict):
    messages: List[BaseMessage]
    emotion: str
    context: str
    route: str


# Emergency function
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    EMERGENCY_CONTACT,
)
from twilio.rest import Client


def emergency_call():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=EMERGENCY_CONTACT,
        from_=TWILIO_FROM_NUMBER,
        url="http://demo.twilio.com/docs/voice.xml",
    )

    return {
        "status": "called",
        "call_sid": call.sid,
    }


def router_node(state: ChatState):
    emotion = state.get("emotion", "").lower()
    user_msg = state["messages"][-1].content.lower()

    if any(
        word in user_msg
        for word in [
            "kill myself",
            "end my life",
            "suicide",
            "want to die",
            "no reason to live",
            "better off dead",
            "hurt myself",
            "end it all",
            "die",
        ]
    ):
        return {"route": "emergency"}

    if emotion in ["suicidal", "severe_distress"]:
        return {"route": "emergency"}

    if emotion in ["sad", "anxious", "stressed", "depressed", "angry"]:
        if len(user_msg.split()) > 4:
            return {"route": "rag"}

    return {"route": "llm"}


# RAG node
def rag_node(state: ChatState):
    user_msg = state["messages"][-1].content

    context = retrieve_context(user_msg)

    return {
        "context": context
    }


# Emergency node
def emergency_node(state: dict):
    print("🚨 Emergency triggered")

    result = emergency_call()

    return {
        **state,
        "emergency": result
    }


# Build agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv("../../.env")

llm = ChatOpenAI(
    model="openai/gpt-4.1",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.github.ai/inference"
)


def call_model(state: ChatState):
    messages = state["messages"]
    emotion = state.get("emotion", "neutral")
    context = state.get("context", "")
    route = state.get("route", "")

    system_prompt = f"""
    You are a mental health support assistant responding AFTER a routing decision has already been made.

    The system has already determined:
    - Emotion: {emotion}
    - Route: {route}
    - Knowledge Context: {context}

    You MUST NOT re-evaluate routing. Only respond appropriately.

    CORE BEHAVIOR

    Be:
    - Warm
    - Human-like
    - Emotionally aware
    - Gently conversational

    Avoid:
    - Robotic phrasing
    - Overly clinical tone
    - Repetitive structures

    ROUTE HANDLING

    1. IF route = "emergency"
    - Respond with urgency, care, and grounding.
    - Encourage reaching out to trusted people or immediate help.
    - Keep responses calm and simple.

    2. IF route = "rag"
    - Use the knowledge context naturally.
    - Blend emotional support with light guidance.
    - Ask gentle reflective questions when useful.

    3. IF route = "llm"
    - Be friendly and conversational.
    - Match the user’s tone.

    GLOBAL SAFETY

    - Never encourage self-harm
    - Never dismiss feelings
    - Never act as a licensed professional
    - Do not provide medical or legal advice

    SCOPE LIMITATION

    Only respond to:
    - Mental health
    - Emotions
    - Stress
    - Light conversation

    If unrelated, say:
    "I’m sorry, I can only help with mental health and emotional well-being topics."

    STYLE

    - Natural and human
    - Not robotic
    - Keep responses concise
    - Match the user's energy level
    """

    final_messages = [SystemMessage(content=system_prompt)] + messages

    try:
        response = llm.invoke(final_messages)

    except Exception as e:
        print("LLM error:", e)

        response = AIMessage(
            content="I’m receiving too many requests right now. Please wait a moment and try again."
        )

    return {
        **state,
        "messages": messages + [response]
    }


def route_decision(state: ChatState):
    return state["route"]


# Build graph
workflow = StateGraph(ChatState)

workflow.add_node("emotion", emotion_node)
workflow.add_node("router", router_node)
workflow.add_node("rag", rag_node)
workflow.add_node("agent", call_model)
workflow.add_node("emergency", emergency_node)

workflow.add_edge(START, "emotion")
workflow.add_edge("emotion", "router")

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag": "rag",
        "llm": "agent",
        "emergency": "emergency"
    }
)

workflow.add_edge("rag", "agent")
workflow.add_edge("agent", END)

app = workflow.compile(checkpointer=memory)

config = {
    "configurable": {
        "thread_id": 1
    }
}