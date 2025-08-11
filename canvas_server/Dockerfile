FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (Code Engine will manage external access)
EXPOSE 8000 

COPY . .

# Ensure port here matches the one exposed above
CMD ["uvicorn", "canvas_server:app", "--host", "0.0.0.0", "--port", "8000"]
