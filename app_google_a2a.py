# server_agent.py
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import json
from typing import List, Dict, Any, Literal

app = FastAPI()

# --- Pydantic Models for A2A types ---
# Define Pydantic models for A2A structures for better type hinting and validation
class TextPart(BaseModel):
    type: Literal["text"] = "text"
    text: str

class Message(BaseModel):
    role: Literal["user", "agent"]
    parts: List[TextPart]

class TaskRequestParams(BaseModel):
    id: str = Field(description="Unique ID for the task")
    sessionId: str = Field(description="Session ID for the conversation")
    message: Message

class TaskRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: Literal["tasks/send"]
    params: TaskRequestParams

class TaskStatus(BaseModel):
    state: Literal["completed", "failed", "running", "cancelled"]
    message: Message

class TaskResponse(BaseModel):
    id: str
    sessionId: str
    status: TaskStatus
    history: List[Message]

# --- Agent Card Endpoint ---
@app.get("/.well-known/agent.json")
async def get_agent_card():
    agent_card = {
        "name": "FastAPIEchoAgent",
        "description": "An A2A agent built with FastAPI that echoes your messages.",
        "url": "http://localhost:8000/",  # Update if running on a different port
        "version": "1.0.0",
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "capabilities": {
            "streaming": False
        },
        "authentication": {
            "schemes": ["none"]
        },
        "skills": [
            {
                "id": "echo_message",
                "name": "Echo Message",
                "description": "Echoes the received message using FastAPI.",
                "tags": ["echo", "reply", "fastapi"],
                "inputModes": ["text"],
                "outputModes": ["text"],
                "examples": ["fastapi echo hello", "fastapi repeat after me"]
            }
        ]
    }
    return agent_card

# --- Task Handling Endpoint ---
@app.post("/tasks/send", response_model=TaskResponse)
async def send_task(task_request: TaskRequest):
    user_message_text = task_request.params.message.parts[0].text
    
    # Simple echo logic
    agent_reply_text = f"FastAPI Echo says: You sent: {user_message_text}"
    agent_reply_message = Message(
        role="agent",
        parts=[TextPart(text=agent_reply_text)]
    )

    # Construct the response Task object
    response_task = TaskResponse(
        id=task_request.params.id,
        sessionId=task_request.params.sessionId,
        status=TaskStatus(
            state="completed",
            message=agent_reply_message
        ),
        history=[
            task_request.params.message,
            agent_reply_message
        ]
    )
    
    return response_task

if __name__ == "__main__":
    import uvicorn
    # Run with: uvicorn server_agent:app --reload --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)