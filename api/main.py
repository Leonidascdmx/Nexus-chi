from fastapi import FastAPI
from orchestrator.main_orchestrator import MainOrchestrator

app = FastAPI(title="HI-NEXUS Gateway", version="1.0.0")
orch = MainOrchestrator()

@app.get("/")
def root():
    return {"status": "HI-NEXUS running"}

@app.get("/run")
def run(goal: str):
    return orch.run(goal)
