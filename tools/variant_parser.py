import re

HGVS_PATTERNS = {
    "cDNA": r"c\.\d+[+-]?\d*[ACGT]?>[ACGT]",
    "protein": r"p\.[A-Z][a-z]{2}\d+[A-Z][a-z]{2}",
    "simple_protein": r"p\.[A-Z]\d+[A-Z]"
}

def extract_hgvs(text: str) -> list:
    """
    Scans a clinical variant string and extracts all matching HGVS cDNA and protein notations.
    """
    variants = []

    for label, pattern in HGVS_PATTERNS.items():
        matches = re.findall(pattern, text)
        for m in matches:
            variants.append({
                "type": label,
                "value": m
            })

    return variants
