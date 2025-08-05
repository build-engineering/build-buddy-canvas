import json
import os

from fastapi import FastAPI
from pydantic import BaseModel, Field
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


def get_code_engine_urls():
    public_url, private_url = None, None
    try:
        # These env variables are automatically injected by Code Engine
        app_name = os.environ['CE_APP']  # Get the application name.
        subdomain = os.environ['CE_SUBDOMAIN']  # Get the subdomain.
        domain = os.environ['CE_DOMAIN']  # Get the domain name.

        public_url = f"https://{app_name}.{subdomain}.{domain}/"
        private_url = f"https://{app_name}.{subdomain}.private.{domain}/" # Construct the private URL.
    except KeyError as e:
        print(f"Error: Required environment variable {e} not found.")
        print("Application may be running locally otherwise required env vars are missing.")
    return public_url, private_url

# --- Agent Card Endpoint ---
@app.get("/.well-known/agent.json")
async def get_agent_card():
    public_url, _ = get_code_engine_urls()
    if not public_url:
        public_url = "http://localhost:8000/"  # Fallback for local development

    agent_card = {
        "name": "FastAPIEchoAgent",
        "description": "An A2A agent built with FastAPI that echoes your messages.",
        "url": public_url,  # Update if running on a different port
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
    # Run with: uvicorn server_agent:app --reload --port 8000
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)