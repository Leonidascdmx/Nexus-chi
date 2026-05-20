import xml.etree.ElementTree as ET

def map_review_stars(status: str) -> int:
    """
    Maps ClinVar ReviewStatus text into a professional 5-star ranking system.
    """
    if not status:
        return 0
    status_lower = status.lower()

    if "practice guideline" in status_lower:
        return 5
    if "reviewed by expert panel" in status_lower:
        return 4
    if "multiple submitters" in status_lower:
        return 3
    if "single submitter" in status_lower:
        return 2
    if "no assertion criteria" in status_lower or "no assertion provided" in status_lower:
        return 1
    return 0

def parse_clinvar_xml(xml_data: str) -> list:
    """
    Parses NCBI ClinVar efetch XML response.
    """
    try:
        root = ET.fromstring(xml_data)
    except Exception:
        return []

    variants = []

    for item in root.findall(".//ClinVarResult-Set/ClinVarAssertionSection/ClinVarSubmission") or root.findall(".//VariationArchive"):
        title = item.findtext(".//VariationName") or item.findtext(".//SimpleAllele/Name")
        
        # Clinical significance
        clinical_sig = item.findtext(".//ClinicalSignificance/Description") or item.findtext(".//Interpretation/Description")
        
        # Review status
        review_status = item.findtext(".//ClinicalSignificance/ReviewStatus") or item.findtext(".//Interpretation/ReviewStatus")
        stars = map_review_stars(review_status)

        # Gene symbol
        gene = item.findtext(".//MeasureSet/Measure/MeasureRelationship/Symbol/ElementValue") or item.findtext(".//GeneList/Gene/Symbol")
        
        variants.append({
            "title": title,
            "clinical_significance": clinical_sig or "Uncertain significance",
            "review_status": review_status or "no assertion criteria provided",
            "review_stars": stars,
            "gene": gene
        })

    return variants
