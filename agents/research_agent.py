import requests

class ResearchAgent:
    """
    ResearchAgent gathers real biomedical summary data directly from the Wikipedia REST API.
    """
    def run(self, gene: str) -> dict:
        print("🔎 Fetching real biomedical data...")

        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{gene}"
        headers = {
            "User-Agent": "HI-NEXUS-Agent/1.0 (clinical-research@hi-nexus.org)"
        }
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                return {"error": "Gene not found"}

            data = res.json()
            return {
                "gene": gene,
                "summary": data.get("extract", ""),
                "source": "Wikipedia"
            }
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
