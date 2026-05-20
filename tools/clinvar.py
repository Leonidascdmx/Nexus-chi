import requests

def fetch_clinvar_variants(gene: str) -> list:
    """
    Queries NCBI ClinVar databases in real time for genetic variants of the target gene,
    extracting clinical significance classifications and review status.
    """
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "clinvar",
        "term": f"{gene}[gene]",
        "retmode": "json",
        "retmax": 5
    }
    
    try:
        res = requests.get(search_url, params=params, timeout=10).json()
        ids = res.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"Error querying ClinVar search: {e}")
        ids = []

    variants = []

    if ids:
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        try:
            details = requests.get(fetch_url, params={
                "db": "clinvar",
                "id": ",".join(ids),
                "retmode": "json"
            }, timeout=10).json()

            for vid in ids:
                item = details.get("result", {}).get(vid, {})
                variants.append({
                    "id": vid,
                    "title": item.get("title"),
                    "clinical_significance": item.get("clinical_significance", "unknown"),
                    "review_status": item.get("review_status", "unknown")
                })
        except Exception as e:
            print(f"Error querying ClinVar summary: {e}")

    return variants
