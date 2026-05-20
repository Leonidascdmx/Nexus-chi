import os
from typing import Dict, Any

from agents.research_agent import ResearchAgent
from agents.bio_agent import BioAgent
from agents.dev_agent import DevAgent

class NexusOrchestrator:
    """
    NexusOrchestrator is the central dispatcher of HI-NEXUS.
    It analyzes incoming prompts, dynamically routes them to the specialized agent,
    and returns synthesized results.
    """
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.bio_agent = BioAgent()
        self.dev_agent = DevAgent()

    def route_request(self, task: str) -> str:
        """
        Routes the task to the most competent agent using semantic keywords
        or LLM routing if keys are available.
        """
        task_lower = task.lower()
        
        # 1. Bio-Agent Routing Indicators
        bio_keywords = [
            "dna", "rna", "protein", "genome", "genetics", "crispr", 
            "insulin", "cellular", "amino acid", "enzyme", "transcribe", 
            "translate", "nucleotide", "biology", "biomedical", "medical"
        ]
        # Match nucleotide sequence directly (e.g. ATGCGCGT)
        has_nucleotide = len(re_seq := [w for w in task.split() if len(w) > 5 and all(c in "ATGCatgc" for c in w)]) > 0
        if has_nucleotide or any(k in task_lower for k in bio_keywords):
            return "bio"

        # 2. Dev-Agent Routing Indicators
        dev_keywords = [
            "write code", "python script", "programming", "algorithm", 
            "fibonacci", "prime number", "function", "debug", "execute code",
            "compile", "subprocess", "calculate", "sandbox"
        ]
        if any(k in task_lower for k in dev_keywords):
            return "dev"

        # 3. Default routing
        return "research"

    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Routes and dispatches the task to the correct agent.
        """
        agent_type = self.route_request(task)
        
        try:
            if agent_type == "bio":
                res = self.bio_agent.run(task)
                return {
                    "status": "success",
                    "routed_agent": "Bio-Agent",
                    "action": "biological_and_molecular_analysis",
                    "content": res["scientific_report"],
                    "data": res
                }
            elif agent_type == "dev":
                res = self.dev_agent.run(task)
                return {
                    "status": "success",
                    "routed_agent": "Dev-Agent",
                    "action": "code_synthesis_and_execution",
                    "content": res["report"],
                    "data": res
                }
            else: # "research"
                res = self.research_agent.run(task)
                return {
                    "status": "success",
                    "routed_agent": "Research-Agent",
                    "action": "web_search_and_data_synthesis",
                    "content": res["report"],
                    "data": res
                }
        except Exception as e:
            return {
                "status": "error",
                "routed_agent": agent_type,
                "action": "orchestration_failure",
                "content": f"Failed during orchestration: {str(e)}",
                "data": {}
            }

if __name__ == "__main__":
    orchestrator = NexusOrchestrator()
    print("Testing HI-NEXUS Orchestration...")
    
    # Test 1: Research
    print("\n--- TEST 1: Research ---")
    r1 = orchestrator.execute_task("Who won the last Formula 1 World Championship?")
    print(f"Routed to: {r1['routed_agent']}")
    
    # Test 2: Bio
    print("\n--- TEST 2: Bio ---")
    r2 = orchestrator.execute_task("Translate the DNA sequence ATGCGATCGATC")
    print(f"Routed to: {r2['routed_agent']}")
    print(f"GC content: {r2['data']['sequence_analysis']}")
    
    # Test 3: Dev
    print("\n--- TEST 3: Dev ---")
    r3 = orchestrator.execute_task("Write a python function to print the first 5 prime numbers and run it")
    print(f"Routed to: {r3['routed_agent']}")
