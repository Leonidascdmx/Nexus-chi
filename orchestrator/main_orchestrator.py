import sys

# Windows console encoding fix for emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agents.research_agent import ResearchAgent
from agents.bio_agent import BioAgent

class MainOrchestrator:
    def __init__(self):
        self.research = ResearchAgent()
        self.bio = BioAgent()

    def analyze_gene(self, gene: str) -> dict:
        print(f"\n🎯 Goal: Analyze {gene}\n")
        research = self.research.run(gene)
        clinical = self.bio.run(research)

        return {
            "input": gene,
            "research": research,
            "clinical_analysis": clinical
        }

if __name__ == "__main__":
    orchestrator = MainOrchestrator()
    result = orchestrator.analyze_gene("ABCC8")
    print("\nResult:")
    print(result)
