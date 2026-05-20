import os
import re
from typing import Dict, Any, List
from skills.web_search import web_search

class BioAgent:
    """
    BioAgent is a specialized agent for biology, medicine, and bioinformatics.
    It can analyze genetic sequences (DNA/RNA) and answer life science inquiries.
    """
    def __init__(self):
        self.name = "Bioinformatics Agent"
        self.description = "Specialized in sequence analysis (transcription, translation, GC-content) and life science research."
        self.codon_table = {
            'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
            'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
            'AAC':'N', 'AAT':'N', 'AAG':'K', 'AAA':'K',
            'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
            'GAC':'D', 'GAT':'D', 'GAG':'E', 'GAA':'E',
            'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
            'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
            'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
            'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
            'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
            'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
            'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
            'CAC':'H', 'CAT':'H', 'CAG':'Q', 'CAA':'Q',
            'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        }

    def transcribe(self, dna: str) -> str:
        """Transcribes DNA to RNA."""
        return dna.upper().replace('T', 'U')

    def translate(self, dna: str) -> str:
        """Translates DNA into protein sequence."""
        dna = dna.upper()
        protein = []
        for i in range(0, len(dna) - (len(dna) % 3), 3):
            codon = dna[i:i+3]
            amino_acid = self.codon_table.get(codon, 'X')
            if amino_acid == '_': # Stop Codon
                protein.append('*')
            else:
                protein.append(amino_acid)
        return "".join(protein)

    def gc_content(self, sequence: str) -> float:
        """Calculates GC content of a genetic sequence."""
        sequence = sequence.upper()
        g_count = sequence.count('G')
        c_count = sequence.count('C')
        total = len(sequence)
        return ((g_count + c_count) / total * 100) if total > 0 else 0.0

    def _call_llm(self, prompt: str, system_instruction: str) -> str:
        """Helper to invoke LLM if configured."""
        if os.environ.get("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
                return model.generate_content(prompt).text
            except Exception:
                pass

        if os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception:
                pass
        return ""

    def run(self, task: str) -> Dict[str, Any]:
        """
        Processes a biological or molecular biology task.
        """
        # Step 1: Detect DNA/RNA genetic sequence inside the prompt
        dna_match = re.search(r'\b[ATGCatgc]{6,}\b', task)
        sequence_analysis = {}
        
        if dna_match:
            dna_seq = dna_match.group(0).upper()
            rna_seq = self.transcribe(dna_seq)
            protein_seq = self.translate(dna_seq)
            gc = self.gc_content(dna_seq)
            sequence_analysis = {
                "detected_dna": dna_seq,
                "transcribed_rna": rna_seq,
                "translated_protein": protein_seq,
                "gc_content_percentage": round(gc, 2)
            }

        # Step 2: Formulate additional background research if needed
        bio_search_results = web_search(task, max_results=3)
        context_str = ""
        for i, res in enumerate(bio_search_results, 1):
            context_str += f"Reference #{i}: {res['title']}\nSummary: {res['snippet']}\n\n"

        # Step 3: LLM Synthesis if possible
        analysis_prompt = f"""
Provide an expert biochemical and bioinformatics analysis on: "{task}"
Search Results Context:
{context_str}

Sequence Analysis pre-calculated (if any):
{sequence_analysis}

Please generate an elite, scientific report detailing the biological mechanism, implications, and details.
"""
        system_instruction = "You are a PhD Bioinformatics and Molecular Biology Agent. Write beautiful, exact, and rigorous scientific markdown."
        
        report = self._call_llm(analysis_prompt, system_instruction)
        
        if not report:
            # High-quality structural markdown fallback
            report = f"""# Bioinformatics Analysis Report: {task}
*Generated by the HI-NEXUS Bio-Agent*

## 1. Scientific Overview
The query relates to biochemical topics. Below is a structured analysis of the subject matter.

"""
            if sequence_analysis:
                report += f"""## 2. Genetic Sequence Characterization
We successfully isolated and analyzed a sequence of nucleotides from your input:
- **Detected DNA Sequence**: `{sequence_analysis['detected_dna']}`
- **GC Content**: `{sequence_analysis['gc_content_percentage']}%`
- **Transcribed RNA**: `{sequence_analysis['transcribed_rna']}`
- **Translated Protein**: `{sequence_analysis['translated_protein']}`

### Sequence Metrics Discussion
A GC content of `{sequence_analysis['gc_content_percentage']}%` has direct implications on the annealing temperature (Tm) and stability of the double helix, typical of certain organic strains or structural requirements.
"""
            else:
                report += """## 2. General Biology / Medical Synthesis
Based on live literature, here are the principal insights:
"""
                for res in bio_search_results:
                    report += f"- **{res['title']}**: {res['snippet']}\n"

            report += """\n## 3. Conclusions & Methods
This analysis provides an initial genomic/biochemical overview. For fully dynamic biochemical paths or protein folding explanations, enable live LLM integration keys.
"""

        return {
            "agent": self.name,
            "sequence_analysis": sequence_analysis,
            "scientific_report": report,
            "references": [{"title": r["title"], "link": r["link"]} for r in bio_search_results]
        }

if __name__ == "__main__":
    agent = BioAgent()
    print("Testing DNA analysis sequence...")
    # DNA sequence of insulin or a tiny test
    res = agent.run("Analyze DNA sequence ATGCGATCGATCGATCGATCGATCGATC")
    print(res["scientific_report"])
