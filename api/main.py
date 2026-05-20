from fastapi import FastAPI
from orchestrator.main_orchestrator import MainOrchestrator
from tools.patient_model import Patient

app = FastAPI(title="HI-NEXUS Clinical API", version="1.0.0")
orch = MainOrchestrator()

@app.get("/")
def root():
    return {"status": "HI-NEXUS clinical API running"}

@app.get("/analyze")
def analyze(gene: str):
    result = orch.analyze_gene(gene)
    return result

@app.get("/analyze_variant")
def analyze_variant(variant: str):
    result = orch.bio.run_variant(variant)
    return result

@app.get("/analyze_patient")
def analyze_patient(variant: str, age: int, glucose: float, insulin: float):
    patient = Patient(age, glucose, insulin)
    result = orch.bio.run_patient(variant, patient)
    return result
