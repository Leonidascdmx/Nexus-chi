import os
import json
import re

class BioAgent:
    """
    BioAgent parses the literature data and matches it against our local curated 
    Congenital Hyperinsulinism variant database (data/chi_variants.json) for molecular insights.
    """
    def __init__(self):
        # Establish path to variants database
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(BASE_DIR, "..", "data", "chi_variants.json")
        
        self.codon_table = {
            'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
            'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
            'AAC':'N', 'AAT':'N', 'AAG':'K', 'AAA':'K',
            'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
            'GAC':'D', 'GAC':'D', 'GAG':'E', 'GAA':'E',
            'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
            'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
            'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
            'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
            'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W',
            'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
            'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
            'CAC':'H', 'CAT':'H', 'CAG':'Q', 'CAA':'Q',
            'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        }

    def load_variants_db(self) -> dict:
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def run(self, data: str) -> str:
        print("🧬 BioAgent executing clinical variant lookup...")
        
        # Load local curated dataset
        db = self.load_variants_db()
        genes_db = db.get("genes", {})
        
        # Identify targeted gene from the literature input
        targeted_gene = None
        for g_key in genes_db.keys():
            if g_key.lower() in data.lower():
                targeted_gene = g_key
                break
        
        # Compile molecular report
        molecular_report = ""
        if targeted_gene:
            gene_info = genes_db[targeted_gene]
            molecular_report = f"""### Curated Genomic Profile: {targeted_gene}
*   **Full Name**: {gene_info['full_name']}
*   **Molecular Function**: {gene_info['description']}
*   **Clinical Relevance & Phenotype**: {gene_info['clinical_relevance']}
*   **Diazoxide Responsiveness**: {'Resistente' if gene_info['resistant_treatments'] else 'Responsivo'}
*   **Recommended Therapies**: {", ".join(gene_info['responsive_treatments'])}
*   **Diazoxide Resistance Class**: {", ".join(gene_info['resistant_treatments']) if gene_info['resistant_treatments'] else "Ninguna (Suele responder)"}

#### 🧬 Cataloged Pathogenic Variants:
"""
            for var in gene_info['common_variants']:
                molecular_report += f"*   **Variant**: `{var['variant']}` | *Class*: **{var['classification']}**\n"
                molecular_report += f"    *Impact*: {var['significance']}\n"
        else:
            molecular_report = """### Curated Genomic Profile: General CHI
*No specific gene locus (ABCC8, KCNJ11, GCK, GLUD1) was identified in the query context. Standard clinical protocol defaults to broad-spectrum genomic testing.*
"""

        # Look for nucleotide sequence calculation needs
        dna_match = re.search(r'\b[ATGCatgc]{6,}\b', data)
        sequence_report = ""
        if dna_match:
            dna_seq = dna_match.group(0).upper()
            rna_seq = dna_seq.replace('T', 'U')
            
            # Translate into protein
            protein = []
            for i in range(0, len(dna_seq) - (len(dna_seq) % 3), 3):
                codon = dna_seq[i:i+3]
                protein.append(self.codon_table.get(codon, 'X'))
            protein_seq = "".join(protein)
            
            g_count = dna_seq.count('G')
            c_count = dna_seq.count('C')
            gc_pct = ((g_count + c_count) / len(dna_seq) * 100) if dna_seq else 0.0
            
            sequence_report = f"""
### [DNA Sequence Verification Metrics]
*   **Isolated DNA Locus**: `{dna_seq}`
*   **RNA Transcript**: `{rna_seq}`
*   **Protein Peptide**: `{protein_seq}`
*   **GC Content Stability**: `{gc_pct:.2f}%`
"""

        # Check if LLM keys are configured
        gemini_key = os.environ.get("GEMINI_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        prompt = f"""
You are an expert AI Bioinformatics and Genetics Agent for HI-NEXUS.
Provide a professional, molecular genetics evaluation.

Retrieved Literature Context:
{data}

Target Locus Database Lookup:
{molecular_report}

Sequence Analytics:
{sequence_report if sequence_report else "No physical nucleotide sequences provided."}
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
                        {"role": "system", "content": "You are an elite clinical geneticist agent."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception:
                pass

        # 3. Fallback: Return structured curated genomic details
        return f"""# HI-NEXUS Clinical Genomic Assessment
*Factual analysis based on PubMed + Curated Local Databases.*

## 1. Curated Locus Overview
{molecular_report}

{sequence_report}

## 2. Clinical Recommendation Summary
Based on the pathogenic profiles, genetic counseling is advised. Recessive locus mutations in SUR1/Kir6.2 necessitate early preparation for Diazoxide-resistance management, including early consideration of molecular PET-imaging (`IMAGE-AI`) to locate possible focal lesions.
"""

if __name__ == "__main__":
    agent = BioAgent()
    print(agent.run("PubMed Lit: we found evidence on ABCC8 hyperinsulinism."))
