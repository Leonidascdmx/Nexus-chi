def interpret_genomic_variant(variant: dict) -> dict:
    """
    Interprets variant molecular impact, separating clinical classifications
    from external database signals.
    """
    hgvs_c = variant.get("hgvs_c")
    hgvs_p = variant.get("hgvs_p")
    classification = variant.get("classification", "unknown")
    
    impact = "unknown"
    if classification == "splicing":
        impact = "Triggers aberrant splice junctions leading to potential intron retention."
    elif classification == "coding":
        impact = "Exonic single-nucleotide polymorphism with risk of amino acid translation disruption."
    elif classification == "protein":
        impact = "Amino acid sequence change impacting localized subunit tertiary folding."

    return {
        "impact_description": impact,
        "is_actionable": classification in ["splicing", "coding", "protein"]
    }
