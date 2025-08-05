FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (Code Engine will manage external access)
EXPOSE 8080 

COPY . .

# Ensure port here matches the one exposed above
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["uvicorn", "app:app_google_a2a", "--host", "0.0.0.0", "--port", "8080"]
#CMD ["uvicorn", "app:app_wxo_agent_connect", "--host", "0.0.0.0", "--port", "8080"]