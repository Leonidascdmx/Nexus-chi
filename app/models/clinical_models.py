from pydantic import BaseModel
from typing import List, Optional

class Patient(BaseModel):
    age_days: int
    glucose: float
    insulin: float

class PatientHistory(BaseModel):
    day: int
    glucose: float
    insulin: float
    treatment: str

class ClinicalSummary(BaseModel):
    diagnosis: str
    severity: str
    confidence: float
    gene: str
    variant: str
    key_action: str

class ClinicalActions(BaseModel):
    primary: str
    secondary: List[str]
    surgery: bool
    imaging_indicated: bool
    imaging_reason: str
    next_steps: List[str]

class GenomicVariant(BaseModel):
    gene: str
    hgvs_c: Optional[str] = None
    hgvs_p: Optional[str] = None
    pathogenicity: str
    review_stars: int
    review_status: str

class ScientificPaper(BaseModel):
    title: str
    journal: str
    year: int
    score: float
    reason: str

class ClinicalResponse(BaseModel):
    summary: ClinicalSummary
    actions: ClinicalActions
    genomics: GenomicVariant
    evidence: List[ScientificPaper]
    timeline: List[PatientHistory]
