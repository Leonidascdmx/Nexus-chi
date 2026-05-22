from fastapi import APIRouter, Query, Body
from app.services.clinical_swarm import ClinicalSwarm
from app.models.clinical_models import ClinicalResponse, Patient
from app.db.patient_repository import save_agent_knowledge

router = APIRouter()
swarm_orchestrator = ClinicalSwarm()

@router.get("/analyze_patient", response_model=ClinicalResponse)
async def analyze_patient(
    variant: str = Query(..., description="HGVS variant cDNA or Protein representation"),
    age: int = Query(..., description="Patient age in days"),
    glucose: float = Query(..., description="Serum glucose reading (mg/dL)"),
    insulin: float = Query(..., description="Serum insulin reading (uU/mL)"),
    patient_id: str = Query("PAT-001", description="Patient unique identifier")
):
    """
    Asynchronously triggers the parallelized Nivel 10 Multi-Agent Swarm analysis.
    Fetches database events, ranks publications, and integrates AgentDB.
    """
    result = await swarm_orchestrator.run_swarm_analysis(
        patient_id=patient_id,
        variant_str=variant,
        age_days=age,
        glucose=glucose,
        insulin=insulin
    )
    return result

@router.post("/feedback")
def submit_clinician_feedback(
    variant: str = Body(..., embed=True),
    gene: str = Body(..., embed=True),
    interpretation: str = Body(..., embed=True),
    stars: int = Body(..., embed=True),
    notes: str = Body("", embed=True),
    clinician: str = Body("Dr. Rodriguez", embed=True)
):
    """
    Allows a clinician to submit feedback, feeding the AgentDB memory base
    with custom overrides and self-learned medical rules.
    """
    save_agent_knowledge(
        variant=variant,
        gene=gene,
        clinical_interpretation=interpretation,
        modified_by=clinician,
        verification_stars=stars,
        learned_rules=f"[Overridden by {clinician}]: {notes}"
    )
    return {
        "status": "success",
        "message": f"Successfully reinforced AgentDB swarm memory for variant {variant}."
    }

@router.get("/history")
def get_history(patient_id: str = Query("PAT-001")):
    """
    Exposes direct historical curves from SQLite database.
    """
    from app.db.patient_repository import get_patient_history
    return get_patient_history(patient_id)
