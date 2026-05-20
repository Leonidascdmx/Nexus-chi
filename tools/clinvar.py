import requests
from tools.variant_parser import extract_hgvs

def fetch_clinvar_variants(gene: str) -> list:
    """
    Queries NCBI ClinVar for variants of the target gene (up to 10),
    performing deep parsing of the titles to extract HGVS cDNA and protein codes.
    """
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "clinvar",
        "term": f"{gene}[gene]",
        "retmode": "json",
        "retmax": 10
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
                title = item.get("title", "")
                
                # 🔍 Extract HGVS from title text
                hgvs = extract_hgvs(title)
                
                variants.append({
                    "clinvar_id": vid,
                    "title": title,
                    "hgvs": hgvs,
                    "clinical_significance": item.get("clinical_significance", "unknown"),
                    "review_status": item.get("review_status", "unknown"),
                    "gene": gene
                })
        except Exception as e:
            print(f"Error querying ClinVar summary: {e}")

    return variants
