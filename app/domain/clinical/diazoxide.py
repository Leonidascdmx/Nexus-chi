def evaluate_diazoxide_response(variant: dict, glucose: float, insulin: float) -> dict:
    """
    Deterministically evaluates expected pediatric Diazoxide therapeutic response.
    Bypasses AI to prevent hallucinated therapeutic paths.
    """
    gene = (variant.get("gene") or "").upper()
    pathogenicity = (variant.get("pathogenicity") or "").lower()

    if gene == "ABCC8" or gene == "KCNJ11":
        if "pathogenic" in pathogenicity:
            return {
                "expected_response": "LOW",
                "action": "Diazoxide trial unlikely to respond - Escalate treatment & consider early surgery",
                "confidence": 0.95
            }

    if glucose < 40.0 and insulin > 10.0:
        return {
            "expected_response": "POOR",
            "action": "Critical hypoglycemic hyperinsulinism - Escalate GIR & plan diazoxide alternative (Octreotide/Dasiglucagon)",
            "confidence": 0.90
        }

    return {
        "expected_response": "UNKNOWN",
        "action": "Initiate standard diazoxide trial under close glycemic monitoring",
        "confidence": 0.60
    }
