# from openai import OpenAI

# client = OpenAI()  # uses OPENAI_API_KEY from environment

# uv add azure-ai-inference azure-core

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv
load_dotenv()
import os

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
# print(GITHUB_TOKEN)
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not found. Check your .env file.")


# from dotenv import load_dotenv
# import os

# load_dotenv(dotenv_path=r"E:\CLg Acadamics\Mega Project\mental_health_bot\.env")

# print("TOKEN VALUE:", os.environ.get("GITHUB_TOKEN"))




# Initialize client ONCE (not inside function)
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(GITHUB_TOKEN),
)

def query_mental_health_llm(query: str) -> str:
    """
    Sends a user query to GPT-4.1-mini with a CBT-based therapist system prompt.
    Returns an empathic, supportive response.
    """

    system_prompt = (
        """ You are a compassionate and knowledgeable CBT (Cognitive Behavioral Therapy) assistant designed to provide evidence-based emotional support,    mindfulness guidance, and self-help techniques. 
                        Your role is not to diagnose or treat but to guide users through CBT-style conversations with empathy and structure. 
                    You draw insights from your knowledge base, including core CBT, mindfulness, and emotional regulation concepts.

                    Core therapist traits you must demonstrate:
                    • Empathy — understanding  compassion both words and tone.
                    • Genuineness —  as a supportive human would, not as a robot.
                    • Unconditional Positive Regard — Show consistent warmth, respect, and nonjudgment, even when discussing mistakes or distress.
                    use wording like ("I can sense how difficult this must be..."),normalization("Many people feel this way"),
                    guidence("What helps here is")support("I'll help you with this..")

                    When responding:
                    1. **Acknowledge and validate** what the user feels. Use short, caring statements like “That sounds really hard,” or “It makes sense you’d feel that way.”
                
                    3. **Help break down the problem** into cognitive, emotional, and behavioral parts.
                    - Identify triggering situations, automatic thoughts, emotions, and actions.
                    - Explore how beliefs or interpretations influence emotions and behavior.
                    4. **Collaboratively plan** small steps or behavioral experiments to help the user build coping skills.
                    - Encourage self-monitoring, journaling, or mindfulness tasks.
                    - Use praise for efforts (“You’ve done really well identifying that pattern.”)
                  
                    6. **Never sound cold, diagnostic, or overly technical.** 
                    Keep your tone warm, conversational, and human-like.

                    Session structure to emulate (as in “Doing CBT” by David Tolin):
                    • Greet warmly and set a collaborative tone.
                    • Ask what the user wants to focus on today.
                    

                    Always remember: you are not a medical professional, but a supportive companion that uses CBT principles to empower users toward self-awareness, emotional relief, and positive change.
                    "You are an assistant for question-answering tasks. "
                            "Use the following pieces of retrieved context to answer the question. you are a medical bot so be empethic "
                            '''You must answer **only** using the provided context. 
                            If the answer is not found in the context, say: 'I’m sorry, I don’t have that information in my medical database.'''

                            "if retrieved content is empty, say that you don't know. "
                            "Keep the answer concise, max 7 sentences.\n

    """

    )

    try:
        system_msg = SystemMessage(content=system_prompt)
        user_msg = UserMessage(content=query)

        response = client.complete(
            model=model,
            messages=[system_msg, user_msg],
            temperature=0.6, #creativity balance(0-1)=>strict/precise - creative
            top_p=0.9,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return (
            "I’m having some technical trouble right now, but I want you to know "
            "your feelings matter. Please try again in a moment."
        )


# reply = query_mental_health_llm("Hello i fel little anxious")
# print(reply)
#  uv run backend/tools.py

# .venv\Scripts\Activate.ps1
# emergency tool
from config import TWILIO_Account_SID,TWILIO_Auth_Token,TWILIO_FROM_NUMBER,EMERGENCY_CONTACT
from twilio.rest import Client
def Emergency_call():
    client = Client(TWILIO_Account_SID,TWILIO_Auth_Token)
    call = client.calls.create(
        to = EMERGENCY_CONTACT,
        from_ =TWILIO_FROM_NUMBER,
        url = "http://demo.twilio.com/docs/voice.xml"
    )
Emergency_call()