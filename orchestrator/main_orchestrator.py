import sys

# Windows console encoding fix for emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agents.research_agent import ResearchAgent
from agents.bio_agent import BioAgent
from tools.clinvar import fetch_clinvar_variants

class MainOrchestrator:
    """
    MainOrchestrator coordinates the active Nivel 3 Clinical Pipeline
    (PubMed E-Utilities + ClinVar E-Utilities -> Multi-Model Validation).
    """
    def __init__(self):
        self.research = ResearchAgent()
        self.bio = BioAgent()

    def analyze_gene(self, gene: str) -> dict:
        print(f"\n🎯 Goal: Analyze {gene}\n")
        
        # 1. Fetch live PubMed scientific publications
        research = self.research.run(gene)
        
        # 2. Fetch live NCBI ClinVar genetic classifications
        variants = fetch_clinvar_variants(gene)
        
        # 3. Perform clinical reasoning and validation checks
        result = self.bio.run(research, variants)

        return result

if __name__ == "__main__":
    orchestrator = MainOrchestrator()
    result = orchestrator.analyze_gene("ABCC8")
    print("\nResult:")
    import json
    print(json.dumps(result, indent=2))
