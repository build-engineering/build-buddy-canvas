from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="LinkedIn Post Generator API")
app.mount("/", StaticFiles(directory="applications", html=True), name="hosted applications")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)