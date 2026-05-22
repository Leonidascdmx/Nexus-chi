from typing import List, Dict
from app.infrastructure.pubmed.pubmed_client import fetch_pubmed_papers
from app.domain.scoring.evidence_ranker import rank_papers
from app.models.clinical_models import ScientificPaper

class ResearchAgent:
    """
    ResearchAgent (Nivel 10): Specialised agent for literature mining and evidence scoring.
    Performs query expansions and ranks PubMed publications with temporal recency decay.
    """
    def __init__(self):
        print("[RESEARCH-AGENT] Initialising PubMed parsing engines...")

    def search_and_rank_literature(self, gene: str, variant_parsed: dict) -> List[ScientificPaper]:
        """
        Executes query expansion, crawls PubMed, and scores evidence dynamically.
        """
        gene_upper = (gene or "unknown").upper()
        
        # ─── 1. Query Expansion ───
        # Expand term to cover CHI synonyms and subunit details
        search_terms = f"{gene_upper} congenital hyperinsulinism"
        if gene_upper == "ABCC8":
            search_terms += " OR SUR1 mutation"
        elif gene_upper == "KCNJ11":
            search_terms += " OR Kir6.2 mutation"
        
        print(f"[RESEARCH-AGENT] Query expanded to: '{search_terms}'")
        
        # ─── 2. Fetch raw PubMed metadata ───
        raw_papers = fetch_pubmed_papers(search_terms)
        
        # ─── 3. Domain Scoring & Recency Decay ───
        scored_papers = rank_papers(raw_papers, gene_upper, variant_parsed)
        
        # Return top ranked papers
        return scored_papers
