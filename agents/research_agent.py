import requests

class ResearchAgent:
    """
    ResearchAgent retrieves real-world clinical papers directly from the official NCBI PubMed E-Utilities.
    """
    def run(self, gene: str) -> dict:
        print("🔎 Fetching PubMed data...")

        # Step 1: Search for PubMed article IDs matching the search term
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": f"{gene} congenital hyperinsulinism",
            "retmode": "json",
            "retmax": 3
        }

        try:
            search_res = requests.get(search_url, params=params, timeout=10).json()
            ids = search_res.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"Error querying PubMed search: {e}")
            ids = []

        articles = []

        # Step 2: Fetch summary metadata for those article IDs
        if ids:
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            try:
                fetch_res = requests.get(fetch_url, params={
                    "db": "pubmed",
                    "id": ",".join(ids),
                    "retmode": "json"
                }, timeout=10).json()

                for uid in ids:
                    article = fetch_res.get("result", {}).get(uid, {})
                    articles.append({
                        "title": article.get("title"),
                        "source": article.get("source"),
                        "pubdate": article.get("pubdate")
                    })
            except Exception as e:
                print(f"Error querying PubMed summary: {e}")

        return {
            "gene": gene,
            "articles": articles
        }
