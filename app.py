from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Sequence, Optional
from dotenv import load_dotenv
import os
from ibm_watsonx_ai import Credentials
from langchain_ibm import ChatWatsonx
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
import uvicorn
from fastapi.responses import StreamingResponse
import uuid
import time
import json
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Watsonx credentials and model setup
if not os.getenv("WATSONX_APIKEY") or not os.getenv("WATSONX_PROJECT_ID"):
    raise ValueError("WATSONX_APIKEY and WATSONX_PROJECT_ID must be set in the environment variables.")

MODEL_ID = "mistralai/mistral-large"
credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key=os.getenv("WATSONX_API_KEY")
)
project_id = os.getenv("WATSONX_PROJECT_ID")

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 500,
    "min_new_tokens": 1
}

llm = ChatWatsonx(
    url=credentials["url"],
    apikey=credentials["apikey"],
    model_id=MODEL_ID,
    project_id=project_id,
    params=parameters,
)

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Post Generator API")

# Define request model
class ChatRequest(BaseModel):
    prompt: str

# Define request model
class Message(BaseModel):
    role: str
    content: str

class ExtraBody(BaseModel):
    thread_id: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = MODEL_ID
    stream: Optional[bool] = False
    extra_body: Optional[ExtraBody] = None

# Define prompts
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical LinkedIn influencer grading a post, Your Job is to just grade the post and give the feedback. Generate critique and recommendations for the user's LinkedIn post."
            "Always provide detailed recommendations, including requests for length, virality, style, tone, reach etc",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a linkedin techie influencer assistant tasked with writing excellent LinkedIn posts."
            " Generate the best and attention grabbing LinkedIn post possible for the user's request. Add emoji's where ever it needed."
            " If the user provides critique, respond with a revised version of your previous attempts.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Create chains
generate_chain = generation_prompt | llm
reflect_chain = reflection_prompt | llm

# Define LangGraph nodes
def generation_node(state: Sequence[BaseMessage]):
    return generate_chain.invoke({"messages": state})

def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    res = reflect_chain.invoke({"messages": messages})
    return [HumanMessage(content=res.content)]

# Build LangGraph
REFLECT = "reflect"
GENERATE = "generate"

builder = MessageGraph()
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)

def should_continue(state: List[BaseMessage]):
    if len(state) > 3:
        return END
    return REFLECT

builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

graph = builder.compile()

# FastAPI endpoint
@app.get("/")
async def root(request: dict):
    return hello_world(request)

@app.get("/hello-world")
async def hello_world(request: dict):
    try:
        return {"response": f"hello world: {request.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request.  Expected request with name parameter with value: {str(e)}")

@app.post("/chat-old/completions")
async def chat_completions(request: ChatRequest):
    try:
        inputs = HumanMessage(content=request.prompt)
        print("INPUT RECEIVED:", request.prompt)
        print("Langgraph Agents Working")
        response = graph.invoke(inputs, debug=False)
        # Extract the final generated post (last message content)
        final_post = response[-1].content if response else "No response generated"
        print("FINAL RESPOSE:", final_post)
        return {"response": final_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    


# Streaming function
async def get_llm_stream(messages: List[Message], model: str, thread_id: str):
    thread_id = thread_id or str(uuid.uuid4())
    inputs = [HumanMessage(content=messages[-1].content)]
    
    # Run LangGraph and get final response
    response = await asyncio.to_thread(graph.invoke, inputs, {"debug": False})
    final_content = response[-1].content if response else "No response generated"
    
    # Send single event with final post
    message_event = {
        "id": f"run-{str(uuid.uuid4())[:6]}",
        "object": "thread.message.delta",
        "thread_id": thread_id,
        "model": model,
        "created": int(time.time()),
        "choices": [{
            "delta": {
                "role": "assistant",
                "content": final_content
            }
        }]
    }
    yield f"event: thread.message.delta\ndata: {json.dumps(message_event)}\n\n"

# FastAPI endpoint
@app.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    X_IBM_THREAD_ID: Optional[str] = Header(None, alias="X-IBM-THREAD-ID")
):
    logger.info(f"Received POST /chat/completions ChatCompletionRequest: {request.json()}")
    thread_id = X_IBM_THREAD_ID or (request.extra_body.thread_id if request.extra_body else None) or str(uuid.uuid4())
    logger.info(f"thread_id: {thread_id}")

    if request.stream:
        return StreamingResponse(
            get_llm_stream(request.messages, request.model, thread_id),
            media_type="text/event-stream"
        )
    else:
        inputs = [HumanMessage(content=request.messages[-1].content)]
        response = await asyncio.to_thread(graph.invoke, inputs, {"debug": False})
        last_message = response[-1].content if response else "No response generated"
        response_data = {
            "id": str(uuid.uuid4()),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": last_message
                },
                "finish_reason": "stop"
            }]
        }
        return response_data

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8081)