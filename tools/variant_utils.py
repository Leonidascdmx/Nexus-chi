def classify_variant(hgvs: str) -> str:
    """
    Classifies an HGVS mutation string into its molecular biology class
    (splicing, coding, protein, or unknown).
    """
    if hgvs.startswith("c."):
        if "+" in hgvs or "-" in hgvs:
            return "splicing"
        return "coding"

    if hgvs.startswith("p."):
        return "protein"

    return "unknown"
