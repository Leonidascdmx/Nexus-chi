import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def search_pubmed(term: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Queries the official NCBI Entrez PubMed database for medical literature.
    
    Args:
        term (str): Search term (e.g., "ABCC8 hyperinsulinism")
        max_results (int): Number of summaries to retrieve
        
    Returns:
        List[Dict[str, str]]: A list of dictionaries with paper 'title', 'pmid', 'journal', and 'url'.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    articles = []

    try:
        # Step 1: Search PubMed for PMIDs matching the search term
        search_url = f"{base_url}/esearch.fcgi?db=pubmed&term={term}&retmode=json&retmax={max_results}"
        search_res = requests.get(search_url, timeout=10)
        
        if search_res.status_code == 200:
            search_data = search_res.json()
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                return []

            # Step 2: Fetch summaries for those PMIDs
            pmid_str = ",".join(pmids)
            summary_url = f"{base_url}/esummary.fcgi?db=pubmed&id={pmid_str}&retmode=json"
            summary_res = requests.get(summary_url, timeout=10)
            
            if summary_res.status_code == 200:
                summary_data = summary_res.json()
                result_map = summary_data.get("result", {})
                
                for pmid in pmids:
                    info = result_map.get(pmid, {})
                    if info:
                        title = info.get("title", "No Title Available")
                        journal = info.get("source", "Unknown Journal")
                        pub_date = info.get("pubdate", "")
                        year = pub_date.split()[0] if pub_date else "Unknown Year"
                        
                        articles.append({
                            "title": title,
                            "pmid": pmid,
                            "journal": f"{journal} ({year})",
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })
    except Exception:
        pass

    return articles

if __name__ == "__main__":
    print("Testing Live PubMed search...")
    res = search_pubmed("ABCC8 Congenital Hyperinsulinism", 3)
    for i, a in enumerate(res, 1):
        print(f"[{i}] {a['title']} - {a['journal']}\n    Link: {a['url']}")
