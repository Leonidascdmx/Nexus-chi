import os
import json

class BioAgent:
    """
    BioAgent parses real research strings, performs target database lookups,
    and returns 100% structured, non-conversational clinical parameters.
    """
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(BASE_DIR, "..", "data", "chi_variants.json")

    def load_variants_db(self) -> dict:
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def run(self, data: str) -> str:
        print("🧬 Real bioanalysis running...")
        
        db = self.load_variants_db()
        genes_db = db.get("genes", {})
        
        # Detect which gene is discussed in the Wikipedia extract
        target_gene = None
        for gene in genes_db.keys():
            if gene.lower() in data.lower():
                target_gene = gene
                break
                
        if not target_gene:
            # Fallback to general lookup if no exact match is found in text
            return json.dumps({
                "error": "No curated hyperinsulinism gene found in research data",
                "extracted_context": data[:200]
            }, indent=2)
            
        gene_info = genes_db[target_gene]
        
        # Construct a 100% factual biological profile
        result = {
            "gene": target_gene,
            "full_name": gene_info["full_name"],
            "molecular_function": gene_info["description"],
            "clinical_impact": gene_info["clinical_relevance"],
            "diazoxide_responsiveness": "RESISTANT" if gene_info["resistant_treatments"] else "RESPONSIVE",
            "recommended_therapies": gene_info["responsive_treatments"],
            "cataloged_pathogenic_variants": [v["variant"] for v in gene_info["common_variants"]]
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
