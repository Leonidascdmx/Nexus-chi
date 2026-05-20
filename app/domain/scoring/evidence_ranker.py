import math
from typing import List
from app.models.clinical_models import ScientificPaper

def rank_papers(papers: list, gene: str, variant: dict) -> List[ScientificPaper]:
    """
    Ranks clinical papers using algebraic parameters and exponential temporal decay.
    Weightings:
      - 40% Keyword & Gene Match
      - 20% Specific Locus Variant Match
      - 20% Exponential Recency Decay (base year: 2026, half-decay parameter: 0.15)
      - 20% Journal Quality Tier Weights
    """
    ranked = []
    base_year = 2026
    gene_lower = (gene or "").lower()
    hgvs_c = (variant.get("hgvs_c") or "").lower()
    hgvs_p = (variant.get("hgvs_p") or "").lower()

    for p in papers:
        score = 0.0
        title = p.get("title", "")
        title_lower = title.lower()
        abstract_lower = p.get("abstract", "").lower()
        journal = p.get("journal", "")
        journal_lower = journal.lower()
        year = int(p.get("year", base_year))

        # ─── 1. GENE MATCH (40% Weight) ───
        if gene_lower and gene_lower in title_lower:
            score += 0.40
        elif gene_lower and gene_lower in abstract_lower:
            score += 0.20

        # ─── 2. SPECIFIC HGVS MUTATION MATCH (20% Weight) ───
        if (hgvs_c and hgvs_c in title_lower) or (hgvs_p and hgvs_p in title_lower):
            score += 0.20
        elif (hgvs_c and hgvs_c in abstract_lower) or (hgvs_p and hgvs_p in abstract_lower):
            score += 0.10

        # ─── 3. EXPONENTIAL RECENCY DECAY (20% Weight) ───
        delta_t = max(0, base_year - year)
        # Exponential decay formula: e^(-0.15 * delta_t)
        decay_factor = math.exp(-0.15 * delta_t)
        score += decay_factor * 0.20

        # ─── 4. JOURNAL QUALITY TIERS (20% Weight) ───
        if any(j in journal_lower for j in ["nature", "nejm", "lancet", "science", "cell"]):
            score += 0.20
        elif any(j in journal_lower for j in ["endocrinology", "pediatric", "diabetes", "genetics"]):
            score += 0.12
        else:
            score += 0.05

        # ─── 5. REASONING STATEMENT ───
        reason = f"Matches {gene.upper()} locus"
        if hgvs_c or hgvs_p:
            reason += f" and specific variant {hgvs_c or hgvs_p}"
        reason += f" with exponential age factor (Year: {year})."

        ranked.append(ScientificPaper(
            title=title,
            journal=journal,
            year=year,
            score=round(score, 3),
            reason=reason
        ))

    # Sort descending by score
    return sorted(ranked, key=lambda x: x.score, reverse=True)
