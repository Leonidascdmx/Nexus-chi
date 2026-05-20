from fastapi import APIRouter, Query
from app.services.clinical_service import ClinicalService
from app.models.clinical_models import ClinicalResponse, Patient

router = APIRouter()
clinical_service = ClinicalService()

@router.get("/analyze_patient", response_model=ClinicalResponse)
def analyze_patient(
    variant: str = Query(..., description="HGVS variant cDNA or Protein representation"),
    age: int = Query(..., description="Patient age in days"),
    glucose: float = Query(..., description="Serum glucose reading (mg/dL)"),
    insulin: float = Query(..., description="Serum insulin reading (uU/mL)"),
    patient_id: str = Query("PAT-001", description="Patient unique identifier")
):
    """
    Triggers complete molecular and pediatric clinical flowsheet analysis.
    Saves readings and retrieves real-time longitudinal physiological history.
    """
    result = clinical_service.run_full_analysis(
        patient_id=patient_id,
        variant_str=variant,
        age_days=age,
        glucose=glucose,
        insulin=insulin
    )
    return result

@router.get("/history")
def get_history(patient_id: str = Query("PAT-001")):
    """
    Exposes direct historical curves from SQLite database.
    """
    from app.db.patient_repository import get_patient_history
    return get_patient_history(patient_id)
