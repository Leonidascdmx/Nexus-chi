import re

HGVS_PATTERNS = {
    "cDNA": r"c\.\d+[+-]?\d*[ACGT]?>[ACGT]",
    "protein": r"p\.[A-Z][a-z]{2}\d+[A-Z][a-z]{2}",
    "simple_protein": r"p\.[A-Z]\d+[A-Z]"
}

def parse_variant(text: str) -> dict:
    """
    Parses a variant string and extracts cDNA, protein, and variant class characteristics.
    """
    variants = []
    for label, pattern in HGVS_PATTERNS.items():
        matches = re.findall(pattern, text)
        for m in matches:
            variants.append({
                "type": label,
                "value": m
            })

    # Classify variant type
    hgvs_c = None
    hgvs_p = None
    
    for v in variants:
        if v["type"] == "cDNA":
            hgvs_c = v["value"]
        elif v["type"] in ["protein", "simple_protein"]:
            hgvs_p = v["value"]

    # Fallback assignments if raw value matches cDNA or protein
    if not hgvs_c and text.startswith("c."):
        hgvs_c = text
    if not hgvs_p and text.startswith("p."):
        hgvs_p = text

    # Variant classification
    classification = "unknown"
    target = hgvs_c or hgvs_p or text
    if target.startswith("c."):
        if "+" in target or "-" in target:
            classification = "splicing"
        else:
            classification = "coding"
    elif target.startswith("p."):
        classification = "protein"

    return {
        "raw": text,
        "hgvs_c": hgvs_c,
        "hgvs_p": hgvs_p,
        "classification": classification
    }
