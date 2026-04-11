import sys
import os
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from env import MisinformationEnv, Action

app = FastAPI(title="Misinformation Detector OpenEnv")
env = MisinformationEnv()

class ActionRequest(BaseModel):
    action_type: str
    content: str

class ResetRequest(BaseModel):
    task_id: Optional[str] = None

@app.get("/")
def root():
    return {
        "name": "misinformation-detector",
        "version": "1.0.0",
        "endpoints": ["/reset", "/step", "/state", "/tasks"]
    }

@app.post("/reset")
def reset(request: ResetRequest = ResetRequest()):
    obs = env.reset(task_id=request.task_id)
    return obs.model_dump()

@app.post("/step")
def step(request: ActionRequest):
    action = Action(
        action_type=request.action_type,
        content=request.content
    )
    result = env.step(action)
    return {
        "observation": result.observation.model_dump(),
        "reward": result.reward.model_dump(),
        "done": result.done,
        "info": result.info
    }

@app.get("/state")
def state():
    return env.state()

@app.get("/tasks")
def list_tasks():
    from tasks import TASKS
    return [
        {
            "id": t["id"],
            "difficulty": t["difficulty"],
            "instruction": t["instruction"]
        }
        for t in TASKS.values()
    ]

def main():
    """Main entry point for openenv validate."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
