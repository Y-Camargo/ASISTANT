from fastapi import FastAPI
import uvicorn

app = FastAPI()
@app.get("/api/tags")
def tags():
    return {"models": [{"name": "mock"}]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11434, log_level="warning")
