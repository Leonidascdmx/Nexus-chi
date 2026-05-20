def chi_full_protocol(patient, gene: str, variant: str, variant_type: str, clinvar: dict) -> dict:
    """
    Computes a complete clinical protocol path for suspected Congenital Hyperinsulinism
    based on live pediatric endocrine guidelines.
    """
    glucose = patient.glucose
    insulin = patient.insulin

    # ─── 1. SCREENING ───
    if glucose < 50:
        hypoglycemia = True
    else:
        return {
            "stage": "screening",
            "diagnosis": "No hypoglycemia",
            "action": "Monitor blood glucose levels regularly"
        }

    # ─── 2. BIOCHEMICAL CONFIRMATION ───
    if insulin > 3 and glucose < 50:
        confirmed_chi = True
    else:
        return {
            "stage": "biochemical",
            "diagnosis": "Hypoglycemia not consistent with hyperinsulinism",
            "action": "Investigate other causes (GH deficiency, cortisol deficiency, metabolic errors)"
        }

    # ─── 3. SEVERITY ───
    if glucose < 40:
        severity = "Severe"
    elif glucose < 50:
        severity = "Moderate"
    else:
        severity = "Mild"

    # ─── 4. GENETIC RISK STRATIFICATION ───
    gene_upper = (gene or "").upper()
    clinvar_sig = (clinvar.get("clinical_significance") or "").lower()

    genetic_risk = "Unknown"

    if gene_upper in ["ABCC8", "KCNJ11"]:
        if "pathogenic" in clinvar_sig or "likely" in clinvar_sig:
            genetic_risk = "High"
        else:
            genetic_risk = "Moderate"

    # ─── 5. THERAPEUTIC RESPONSE PREDICTION: DIAZOXIDE ───
    diazoxide = {
        "trial": True,
        "expected_response": "Unknown",
        "action": ""
    }

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

    # ─── 6. SECOND-LINE THERAPEUTICS ───
    second_line = []

    if diazoxide["expected_response"] in ["Very low", "Low"]:
        second_line = [
            "Octreotide",
            "Dasiglucagon",
            "Continuous feeding"
        ]

    # ─── 7. SURGICAL RECOMMENDATION ───
    surgery = {
        "indicated": False,
        "reason": ""
    }

    if gene_upper in ["ABCC8", "KCNJ11"] and ("pathogenic" in clinvar_sig or "likely" in clinvar_sig):
        if severity == "Severe":
            surgery["indicated"] = True
            surgery["reason"] = "High probability of focal or diffuse KATP-CHI disease"

    # ─── 8. IMAGING PROTOCOLS (18F-DOPA PET/CT) ───
    imaging = {
        "PET_scan": False,
        "reason": ""
    }

    if surgery["indicated"]:
        imaging["PET_scan"] = True
        imaging["reason"] = "Highly indicated to differentiate focal vs diffuse CHI before surgical mapping"

    # ─── 9. COMPLETE STRATIFIED OUTPUT ───
    return {
        "stage": "complete",
        "diagnosis": "Congenital Hyperinsulinism",
        "severity": severity,
        "genetics": {
            "gene": gene_upper,
            "variant": variant,
            "risk": genetic_risk
        },
        "treatment": {
            "diazoxide": diazoxide,
            "second_line": second_line,
            "surgery": surgery
        },
        "imaging": imaging,
        "next_steps": [
            "Monitor glucose continuously (CGM / frequent checks)",
            "Adjust fluid and GIR therapy based on glycemic response",
            "Refer immediately to a specialized hyperinsulinism reference center"
        ]
    }
