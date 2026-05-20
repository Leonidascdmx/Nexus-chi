import requests
import re

class ResearchAgent:
    """
    ResearchAgent conducts real-world clinical and genetic literature inquiries
    directly using the live Wikipedia Page Summary API with appropriate headers.
    """
    def run(self, query: str) -> str:
        print("🔎 Real research running...")
        
        # Clean query: extract gene name (e.g. ABCC8, KCNJ11, GCK, GLUD1) or use first word
        gene_match = re.search(r'\b(ABCC8|KCNJ11|GCK|GLUD1)\b', query, re.IGNORECASE)
        target = gene_match.group(1).upper() if gene_match else query.split()[0]
        
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{target}"
        headers = {
            "User-Agent": "HI-NEXUS-Agentic-Platform/1.0 (clinical-research@hi-nexus.org)"
        }
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return data.get("extract", "No info found")
        except Exception as e:
            return f"Error fetching data: {str(e)}"
            
        return "No info found on Wikipedia"
