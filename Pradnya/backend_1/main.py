# step 5
from fastapi.middleware.cors import CORSMiddleware

# step1- setup  fastapi backend
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# step 4) connecting llm
from backend.ai_agent import graph,SYSTEM_PROMPT,parse_response


# step2 - recieve and validate request from frontend
class Query(BaseModel):
    message:str 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3002"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(query:Query):
    # AI agent
    # static
    # response = "This is from backend"

    # bot
    
    inputs = {"messages":[("system",SYSTEM_PROMPT),("user",query.message)]}
    stream = graph.stream(inputs,stream_mode="updates")
    tool_called,final_response = parse_response(stream)
    
    

    # step3 - send responce to frontend
    # return response
    return {"tool used":tool_called,
    "response":final_response}




if __name__ == "_main_":
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)


# uv run uvicorn backend.main:app --reload


# “Watch my code files, and if I change anything, automatically restart the server.”