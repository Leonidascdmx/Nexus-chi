class Patient:
    """
    Patient models clinical and biochemical parameters of neonates/infants
    presenting with suspected hyperinsulinemic hypoglycemia.
    """
    def __init__(self, age_days: int, glucose: float, insulin: float):
        self.age_days = age_days
        self.glucose = glucose
        self.insulin = insulin

    def to_dict(self) -> dict:
        return {
            "age_days": self.age_days,
            "glucose_mg_dl": self.glucose,
            "insulin_uU_ml": self.insulin
        }

def assess_severity(glucose: float, insulin: float) -> str:
    """
    Determines severity of hyperinsulinemic hypoglycemia using established
    pediatric endocrine diagnostic ranges.
    """
    if glucose < 40 and insulin > 10:
        return "High"
    elif glucose < 50:
        return "Moderate"
    return "Low"
