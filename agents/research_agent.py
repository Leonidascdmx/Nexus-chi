import os
import re
from typing import Dict, Any, List
from skills.web_search import web_search

class ResearchAgent:
    """
    ResearchAgent is responsible for gathering information, performing web searches,
    analyzing findings, and presenting a synthesized report on a given topic.
    """
    def __init__(self):
        self.name = "Research Agent"
        self.description = "Specialized in search formulation, deep data retrieval, and factual synthesis."

    def _call_llm(self, prompt: str, system_instruction: str = "You are a professional research agent.") -> str:
        """
        Attempts to call an LLM (Gemini, OpenAI, or Anthropic) if keys are present.
        Otherwise, returns a structured analytical synthesis of the search results.
        """
        # 1. Google Gemini API
        if os.environ.get("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                pass

        # 2. OpenAI API
        if os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception:
                pass

        # 3. Fallback Heuristics Aggregator (No LLM key)
        # Synthesize results into a beautifully formatted report manually
        return ""

    def run(self, task: str) -> Dict[str, Any]:
        """
        Executes the research task.
        """
        # Step 1: Extract keywords for search query formulation
        clean_task = re.sub(r'[^\w\s]', '', task)
        words = [w for w in clean_task.split() if len(w) > 3]
        search_query_str = " ".join(words[:5]) if words else task
        
        # Step 2: Perform search
        search_results = web_search(search_query_str, max_results=4)
        
        # Step 3: Format the context for synthesis
        context_str = ""
        for i, res in enumerate(search_results, 1):
            context_str += f"Result #{i}:\nTitle: {res['title']}\nURL: {res['link']}\nSnippet: {res['snippet']}\n\n"

        # Step 4: Synthesize report
        prompt = f"""
Synthesize a comprehensive research report on the following topic/task: "{task}"
Below are the search results retrieved for the query "{search_query_str}":

{context_str}

Please generate a professional, highly readable markdown report with:
1. Executive Summary
2. Core Findings & Technical Highlights
3. Source References (with URLs from the search results)
"""

        system_instruction = "You are a professional, elite AI Research Agent. Output beautiful, structured markdown."
        
        report = self._call_llm(prompt, system_instruction)
        
        # Heuristic fallback if LLM was not available or failed
        if not report:
            report = f"""# Research Report: {task}
*Note: This report was compiled using HI-NEXUS heuristic synthesis.*

## 1. Executive Summary
An initial investigation was launched on the topic of **"{task}"**. Search queries returned {len(search_results)} relevant references.

## 2. Core Findings & Information
Here is the aggregated information retrieved from live sources:

"""
            for res in search_results:
                report += f"### {res['title']}\n"
                report += f"- **Key Fact**: {res['snippet']}\n"
                report += f"- **Source Link**: [{res['link']}]({res['link']})\n\n"
                
            report += """## 3. Conclusion & Recommendations
The subject exhibits active discussion and development. For fully synthesized insights, configure either `GEMINI_API_KEY` or `OPENAI_API_KEY` in your environment.
"""

        return {
            "agent": self.name,
            "query": search_query_str,
            "results_count": len(search_results),
            "report": report,
            "sources": [{"title": r["title"], "link": r["link"]} for r in search_results]
        }

if __name__ == "__main__":
    agent = ResearchAgent()
    print("Running Research Agent locally...")
    result = agent.run("Latest breakthroughs in quantum computing architecture")
    print(result["report"])
