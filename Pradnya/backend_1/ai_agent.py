# uv add langchain
# import langchain
# print(langchain.__version__)
from langchain.tools import tool
from tools import query_mental_health_llm
@tool
def ask_mental_bot(query: str) -> str:
    """
    Use this tool for empathetic, non-crisis mental health conversations.
    This includes emotional distress such as anxiety, sadness, stress, loneliness,
    or feeling overwhelmed WITHOUT suicidal intent.
    The tool should provide validation, reflection, gentle questioning,
    and CBT-style coping guidance in a warm, non-judgmental tone.
    """
    # connect with gpt
    return query_mental_health_llm(query)

# emergency tool
from tools import Emergency_call
@tool
def Emergency_tool():
    """
    Use this tool ONLY when the user expresses suicidal thoughts, self-harm intent,
    desire to die, or immediate danger to themselves.
    This tool must be called instead of providing therapy, reassurance, or advice.
    It should prioritize safety, crisis resources, and urgent real-world help.
    """
    return Emergency_call()


@tool
def nearby_therapist_tool(query: str) -> str:
    """
    Use this tool when the user asks to find, contact, or talk to a real human
    mental health professional such as a therapist, counselor, or psychologist.
    This includes requests for nearby, local, offline, or in-person help.
    The tool should help guide the user toward real-world professional resources.
    """
    return "finding therapist"

# step1 : create AI agent and link to backend
from langgraph.prebuilt import create_react_agent

MyTools = [ask_mental_bot,Emergency_tool,nearby_therapist_tool]
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

llm = ChatOpenAI(
    model="meta-llama/llama-3-8b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

graph = create_react_agent(llm, tools=MyTools)
# now design the agent- we have llm this llm should decide it given query is a general chat or emergency or need rag
SYSTEM_PROMPT = """You are a mental-health conversation router and safety controller.

Your primary role is to ROUTE messages to the correct tool.
You must never provide therapy directly yourself.
Your role is to decide how the user's message should be handled.

You have access to the following tools:
1. ask_mental_bot – for empathetic, therapeutic conversation
2. Emergency_tool – for crisis situations involving self-harm or suicide risk
3. nearby_therapist_tool – for requests to find real human professionals

You must strictly follow these rules:

ROUTING RULES:

A. NORMAL CONVERSATION
If the user's message is casual, informational, neutral, or everyday chat
(e.g., greetings, general questions, light emotions),
respond directly in a friendly but brief manner.
Do NOT provide therapy.

B. EMOTIONAL DISTRESS (NON-CRISIS)
If the user expresses sadness, anxiety, loneliness, overwhelm, stress,
or emotional struggle WITHOUT suicidal intent,
DO NOT respond directly.
You MUST call ask_therapist_tool.

C. CRISIS / SELF-HARM
If the user expresses:
- suicidal thoughts
- desire to die
- self-harm intent
- hopelessness combined with danger
Immediately call emergency_tool.
DO NOT attempt therapy or reassurance yourself.

D. REAL-WORLD HELP REQUEST
If the user asks to:
- talk to a real therapist
- find nearby mental health professionals
- get offline help
Call nearby_therapist_tool.

IMPORTANT CONSTRAINTS:
- Never combine multiple tools in one turn.
- Never provide therapy yourself.
- Never override the emergency tool.
- When unsure between normal vs emotional, prefer ask_therapist_tool.
- Safety has higher priority than user preference.

Your responses must be calm, respectful, and minimal.
Your intelligence is measured by correct routing, not verbosity.
'''You must answer **only** regarding mental health and stress relife help context or have a general conversation. 
        If the query is from a perticular context other than mental health, say: 'I’m sorry, I don’t have that information in my mental health database.'''
"""

def parse_response(stream):
    tool_called = None
    final_response = None

    for update in stream:
        agent_data = update.get("agent")
        if not agent_data:
            continue

        messages = agent_data.get("messages", [])
        for msg in messages:
            # Detect tool call
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_called = msg.tool_calls[0]["name"]

            # Detect normal assistant message
            if hasattr(msg, "content") and msg.content:
                final_response = msg.content

    return tool_called, final_response


if __name__ == "__main__":
    while True:
        user_input = input("User:")
        print(f"Recieved user input:{user_input[:200]}...")
        inputs = {"messages":[("system",SYSTEM_PROMPT),("user",user_input)]}
        stream = graph.stream(inputs,stream_mode="updates")
        tool_called,final_response = parse_response(stream)
        print("Tool Called:",tool_called)
        print("Response:",final_response)

        # for s in stream:
        #     print(s)

        # result = graph.invoke(inputs)
        # print(result)



# ---------------------------------------------------------------------------------------------------
# if __name__ == "__main__":
# What this means
# Python files can be:
# run directly
# imported into another file
# This line means:
# “Only run the code below if this file is executed directly, not imported.”

# WHY DO WE CALL graph.stream() AT ALL?
# You are NOT calling stream() because the user is typing
# You are calling stream() because the AGENT is thinking in steps
# That’s the key.
# Think of your agent as a decision pipeline
# Your agent does multiple steps internally:
# Read SYSTEM_PROMPT
# Read user message
# Decide:
# normal chat?
# therapist?
# emergency?
# Possibly call a tool
# Get tool result
# Decide next step
# Produce final response
# This is NOT one operation.
# It is a sequence of steps.
# Two ways to run this pipeline
# OPTION 1 — invoke() (no streaming)
# result = graph.invoke(input)
# print(result)
# What happens:
# Agent does everything silently
# You see only the final output
# You have no idea:
# which tool was chosen
# why
# when
# This is like:
# “Just give me the final answer, don’t show your work.”
# OPTION 2 — stream() (what you’re using)
# stream = graph.stream(input, stream_mode="updates")
# for s in stream:
#     print(s)
# What happens:
# Agent runs step by step
# After EACH step, it emits an update
# You see:
# routing decision
# tool call
# tool output
# final message
# This is like:
# “Show me how you decided.”

# for s in stream:
#     print(s)
# Means:
# “Every time the agent finishes ONE internal step, give it to me.”