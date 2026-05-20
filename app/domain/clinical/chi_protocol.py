def evaluate_chi_screening(glucose: float, insulin: float) -> dict:
    """
    Confirms hypoglycemic hyperinsulinism biochemically.
    """
    if glucose >= 50:
        return {
            "eligible": False,
            "reason": "Serum glucose level is normal (>= 50 mg/dL). No hypoglycemia detected."
        }
    if insulin <= 3.0:
        return {
            "eligible": False,
            "reason": "Serum insulin is appropriate suppressed (<= 3 uU/mL) for hypoglycemic state."
        }
    return {
        "eligible": True,
        "reason": "Biochemically consistent with Congenital Hyperinsulinism."
    }

def chi_full_protocol(age_days: int, glucose: float, insulin: float, gene: str, variant_type: str, pathogenicity: str) -> dict:
    """
    Pediatric clinical flowsheet engine for Congenital Hyperinsulinism.
    Determines severity, genetic risk vectors, therapeutic outcomes, and imaging.
    """
    # ─── 1. BIOCHEMICAL SCREENING ───
    screening = evaluate_chi_screening(glucose, insulin)
    if not screening["eligible"]:
        return {
            "stage": "screening_failed",
            "diagnosis": "Non-CHI Hypoglycemia",
            "severity": "Mild",
            "next_steps": [
                "Investigate other causes of infant hypoglycemia (e.g. GH deficiency, cortisol deficiency, metabolic errors)",
                "Support blood glucose with appropriate feeding or intravenous glucose infusion"
            ]
        }

    # ─── 2. SEVERITY STRATIFICATION ───
    if glucose < 40.0:
        severity = "Severe"
    elif glucose < 50.0:
        severity = "Moderate"
    else:
        severity = "Mild"

    # ─── 3. GENETIC RISK STRATIFICATION ───
    gene_upper = (gene or "").upper()
    path_lower = (pathogenicity or "").lower()
    
    is_katp_gene = gene_upper in ["ABCC8", "KCNJ11"]
    is_pathogenic = "pathogenic" in path_lower or "likely pathogenic" in path_lower
    
    genetic_risk = "High" if is_katp_gene and is_pathogenic else "Moderate"

    # ─── 4. TRATAMIENTO: DIAZÓXIDO RESPONSE PREDICTION ───
    diazoxide = {"trial": True, "expected_response": "Unknown", "action": ""}
    if genetic_risk == "High":
        if variant_type == "splicing":
            diazoxide["expected_response"] = "Very low"
            diazoxide["action"] = "Skip or short trial → evaluate surgery"
        else:
            diazoxide["expected_response"] = "Low"
            diazoxide["action"] = "Trial with extreme caution and high glucose infusion rate (GIR)"
    else:
        diazoxide["expected_response"] = "Moderate"
        diazoxide["action"] = "Standard diazoxide trial recommended"

    # ─── 5. SEGUNDAS LÍNEAS ───
    second_line = []
    if diazoxide["expected_response"] in ["Very low", "Low"]:
        second_line = ["Octreotide", "Dasiglucagon", "Continuous feeding"]

    # ─── 6. CIRUGÍA E IMAGEN (18F-DOPA PET/CT) ───
    surgery_indicated = False
    surgery_reason = "No indication for primary surgical intervention."
    if is_katp_gene and is_pathogenic and severity == "Severe":
        surgery_indicated = True
        surgery_reason = "High probability of severe, diffuse or focal KATP-CHI disease unresponsive to medical management."

    imaging_indicated = False
    imaging_reason = "Not indicated for localized imaging."
    if surgery_indicated:
        imaging_indicated = True
        imaging_reason = "Highly indicated 18F-DOPA PET/CT scan to differentiate focal vs diffuse CHI before surgical mapping."

    return {
        "stage": "complete",
        "diagnosis": "Severe Congenital Hyperinsulinism" if severity == "Severe" else "Congenital Hyperinsulinism",
        "severity": severity,
        "genetic_risk": genetic_risk,
        "treatment": {
            "diazoxide": diazoxide,
            "second_line": second_line,
            "surgery": {
                "indicated": surgery_indicated,
                "reason": surgery_reason
            }
        },
        "imaging": {
            "indicated": imaging_indicated,
            "reason": imaging_reason
        },
        "next_steps": [
            "Monitor glucose continuously (CGM / frequent checks)",
            "Adjust fluid and GIR therapy based on glycemic response",
            "Refer immediately to a specialized hyperinsulinism reference center"
        ]
    }
