class BioAgent:
    """
    BioAgent performs clinical diagnostics matching genetic research with a multi-gene database.
    """
    def run(self, research_data: dict) -> dict:
        print("🧬 Clinical reasoning...")

        gene = research_data.get("gene", "")
        articles = research_data.get("articles", [])

        gene_upper = gene.upper()

        # Level 2 Scaled Gene Locus Database
        gene_db = {
            "ABCC8": {
                "condition": "Congenital Hyperinsulinism (CHI)",
                "mechanism": "KATP channel dysfunction → unregulated insulin secretion",
                "risk": "High",
                "treatment": [
                    "Diazoxide (first-line)",
                    "Octreotide",
                    "Partial pancreatectomy (if focal)"
                ]
            },
            "KCNJ11": {
                "condition": "Congenital Hyperinsulinism (CHI)",
                "mechanism": "Kir6.2 channel mutation affecting insulin regulation",
                "risk": "High",
                "treatment": [
                    "Diazoxide",
                    "Surgery (in severe cases)"
                ]
            },
            "GLUD1": {
                "condition": "Hyperinsulinism/Hyperammonemia Syndrome",
                "mechanism": "Gain-of-function in glutamate dehydrogenase",
                "risk": "Moderate",
                "treatment": [
                    "Protein-restricted diet",
                    "Diazoxide"
                ]
            },
            "GCK": {
                "condition": "Glucokinase-related hyperinsulinism",
                "mechanism": "Altered glucose sensing",
                "risk": "Variable",
                "treatment": [
                    "Diazoxide",
                    "Monitoring"
                ]
            }
        }

        if gene_upper in gene_db:
            base = gene_db[gene_upper]

            return {
                "gene": gene_upper,
                "condition": base["condition"],
                "mechanism": base["mechanism"],
                "risk_level": base["risk"],
                "treatment": base["treatment"],
                "evidence": articles
            }

        return {
            "gene": gene,
            "condition": "Unknown",
            "risk_level": "Unknown",
            "evidence": articles
        }
