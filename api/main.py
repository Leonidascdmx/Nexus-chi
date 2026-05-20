import os
import json
from fastapi import FastAPI
from orchestrator.main_orchestrator import MainOrchestrator

app = FastAPI(title="HI-NEXUS Gateway", version="1.0.0")
orch = MainOrchestrator()

# Establish path to the foundation JSON database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "hi_nexus_data.json")

def load_foundation_data() -> dict:
    """Helper to safely load the unified proposal dataset."""
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

@app.get("/")
def root():
    return {
        "status": "HI-NEXUS running",
        "description": "Hyperinsulinism Intelligence Network for Universal eXploration & Solutions Gateway"
    }

@app.get("/run")
def run(goal: str):
    return orch.run(goal)

@app.get("/api/data")
def get_all_data():
    """Serves the entire unified clinical and operational proposal dataset."""
    return load_foundation_data()

@app.get("/api/modules")
def get_modules():
    """Serves the 7 research modules and their clinical parameters."""
    return load_foundation_data().get("modules", [])

@app.get("/api/staff")
def get_staff():
    """Serves the comprehensive existing staff and planned hires directory."""
    return load_foundation_data().get("staff", [])

@app.get("/api/phases")
def get_phases():
    """Serves the 4-phase master timeline execution roadmap."""
    return load_foundation_data().get("phases", [])
