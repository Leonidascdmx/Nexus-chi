import os
import re
from skills.pubmed_client import search_pubmed
from skills.web_search import search

class ResearchAgent:
    """
    ResearchAgent parses the clinical goal, extracts genes, and queries PubMed
    as well as general medical search indices for real-world research.
    """
    def run(self, query: str) -> str:
        print(f"🔎 ResearchAgent conducting PubMed & medical search for: {query}")
        
        # 1. Detect if any known hyperinsulinism gene is mentioned
        genes_found = []
        for gene in ["ABCC8", "KCNJ11", "GCK", "GLUD1", "HADH", "SLC16A1"]:
            if gene.lower() in query.lower():
                genes_found.append(gene)

        target_term = query
        if genes_found:
            target_term = f"{genes_found[0]} congenital hyperinsulinism"

        # 2. Run real PubMed query
        print(f"   -> Querying official PubMed database for '{target_term}'...")
        pubmed_articles = search_pubmed(target_term, max_results=3)

        # 3. Compile a real literature log
        literature_report = "### [PubMed Lit-Finder Results]\n"
        if pubmed_articles:
            for art in pubmed_articles:
                literature_report += f"*   **Paper**: {art['title']}\n"
                literature_report += f"    *Journal*: {art['journal']} | [Read PMID {art['pmid']}]({art['url']})\n\n"
        else:
            literature_report += "*No active PubMed articles returned. Querying general index.*\n\n"
            search_summary = search(query, max_results=2)
            literature_report += search_summary

        # Check if LLM keys are configured for synthesis
        gemini_key = os.environ.get("GEMINI_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        prompt = f"""
You are an expert AI Research Agent for HI-NEXUS specializing in Congenital Hyperinsulinism (CHI).
Compile a professional markdown literature synthesis.

Goal Query: "{query}"
Retrieved Literature:
{literature_report}
"""

        # 1. Try Gemini
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                pass
                
        # 2. Try OpenAI
        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional clinical research agent."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception:
                pass

        # 3. Fallback: Return structured factual report
        return f"""# HI-NEXUS Scientific Literature Synthesis
*Real-time PubMed lookup compiled by ResearchAgent.*

## 1. Scope of Inquiry
Analyzing literature regarding: **"{query}"**
Target gene associations identified: {", ".join(genes_found) if genes_found else "General clinical terms"}

## 2. Active PubMed Bibliography
{literature_report}
"""

if __name__ == "__main__":
    agent = ResearchAgent()
    print(agent.run("ABCC8 mutations treatments"))
