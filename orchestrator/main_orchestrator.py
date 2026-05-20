import sys

# Windows console encoding fix for emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

class MainOrchestrator:
    """
    MainOrchestrator coordinates the active Level 2 Clinical Pipeline
    (PubMed E-Utilities -> Multi-Gene Locus Classification).
    """
    def __init__(self):
        from agents.research_agent import ResearchAgent
        from agents.bio_agent import BioAgent

        self.research = ResearchAgent()
        self.bio = BioAgent()

    def analyze_gene(self, gene: str) -> dict:
        print(f"\n🎯 Goal: Analyze {gene}\n")
        research = self.research.run(gene)
        clinical = self.bio.run(research)

        return {
            "input": gene,
            "clinical_analysis": clinical
        }

if __name__ == "__main__":
    orchestrator = MainOrchestrator()
    result = orchestrator.analyze_gene("ABCC8")
    print("\nResult:")
    import json
    print(json.dumps(result, indent=2))
