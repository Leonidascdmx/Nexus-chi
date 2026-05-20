import sys

# Windows console encoding fix for emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agents.research_agent import ResearchAgent
from agents.bio_agent import BioAgent
from agents.dev_agent import DevAgent

class MainOrchestrator:
    def __init__(self):
        self.research = ResearchAgent()
        self.bio = BioAgent()
        self.dev = DevAgent()

    def run(self, goal: str):
        print(f"\n🎯 Goal: {goal}\n")

        research_data = self.research.run(goal)
        bio_data = self.bio.run(research_data)
        dev_output = self.dev.run(bio_data)

        return {
            "research": research_data,
            "bio": bio_data,
            "dev": dev_output
        }


if __name__ == "__main__":
    orchestrator = MainOrchestrator()
    result = orchestrator.run("Analyze hyperinsulinism treatments")
    print(result)
