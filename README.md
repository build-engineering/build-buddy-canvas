# Canvas builder for Build Buddy using WxO Agent Connect

Build Buddy uses this repo/container to power the canvas used when building its agentic AI applications

This project was initially based off [Dheeraj-Arremsetty's wx.orchestrate Agents BuilderLibrary](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library)

## 🎯 Key Objective
Showcase how WxO can seamlessly connect to and orchestrate external agents through the **Agent Connect** feature, enabling hybrid AI workflows that combine WxO's capabilities with external specialized agents.

## 🚀 Workflow Overview

### Step 1: Create External Agent
- Build a LangGraph agent that generates LinkedIn posts
- Expose it as a REST API with `/chat/completions` endpoint
- Implement both streaming and non-streaming responses

### Step 2: Deploy to IBM Code Engine
- Containerize the application using Docker
- Deploy to IBM Code Engine for cloud hosting
- Ensure the API is publicly accessible

### Step 3: Connect via WxO Agent Connect
- Navigate to WxO Portal
- Use the **Agent Connect** feature
- Configure connection to the external agent
- Test the integration

## 🛠️ Implementation Details

### External Agent Features
- **LangGraph Workflow**: Iterative post generation and refinement
- **IBM Watsonx Integration**: Powered by Watsonx AI models
- **REST API**: Standard `/chat/completions` endpoint
- **Response Types**: Streaming (`text/event-stream`) and JSON
- **LinkedIn Optimization**: Professional posts with emojis and hashtags

### API Specification
```
POST /chat/completions
Content-Type: application/json
X-IBM-THREAD-ID: {thread_id} (for streaming)

Body: {
  "messages": [
    {"role": "user", "content": "Generate a post about AI trends"}
  ],
  "stream": true/false
}
```

## 📋 Prerequisites

- Python 3.8+
- IBM Watsonx API key and project ID
- IBM Code Engine account
- Git and Docker installed

## ⚙️ Setup & Deployment

### 1. Local Development
```bash
# Clone and setup
git clone <repository-url>
cd 4.0-External-Agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with:
# wx_api_key=your_watsonx_api_key_here
# wx_project_id=your_watsonx_project_id_here

# Run locally
python app.py
```

### 2. IBM Code Engine Deployment
```bash
# Build and deploy (manual process)
# Follow IBM Code Engine documentation for deployment
```

### 3. WxO Agent Connect Configuration
1. **Access WxO Portal**: Navigate to your Watsonx Orchestrate workspace
2. **Agent Connect**: Select the Agent Connect feature
3. **Configure Connection**: 
   - Enter your external agent's API endpoint
   - Set authentication if required
   - Test the connection
4. **Integration**: The external agent is now available in WxO workflows

## 🧪 Testing

### Test External Agent Directly
```bash
# Streaming request
curl -X POST "http://localhost:8000/chat/completions" \
-H "Content-Type: application/json" \
-H "X-IBM-THREAD-ID: test-thread-123" \
-d '{"messages": [{"role": "user", "content": "Write about AI innovation"}], "stream": true}'

# Non-streaming request
curl -X POST "http://localhost:8000/chat/completions" \
-H "Content-Type: application/json" \
-d '{"messages": [{"role": "user", "content": "Write about AI innovation"}]}'
```