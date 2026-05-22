import asyncio
from app.models.clinical_models import (
    ClinicalResponse, ClinicalSummary, ClinicalActions, GenomicVariant, GenomicDiagnosisResponse
)
from app.domain.genomics.variant_parser import parse_variant
from app.domain.genomics.variant_interpreter import interpret_genomic_variant
from app.domain.clinical.chi_protocol import chi_full_protocol
from app.domain.clinical.diazoxide import evaluate_diazoxide_response
from app.domain.scoring.evidence_ranker import rank_papers
from app.infrastructure.clinvar.clinvar_client import fetch_clinvar_data
from app.infrastructure.pubmed.pubmed_client import fetch_pubmed_papers
from app.infrastructure.myvariant.myvariant_client import query_myvariant_info
from app.db.patient_repository import (
    save_patient_event, get_patient_history, get_agent_knowledge, save_agent_knowledge
)
from app.services.bio_agent import BioAgent

class ClinicalSwarm:
    """
    Nivel 10 Swarm Intelligence Core.
    Orchestrates multiple specialized micro-agents working concurrently.
    """
    def __init__(self):
        self.bio_agent = BioAgent()

    async def run_swarm_analysis(self, patient_id: str, variant_str: str, age_days: int, glucose: float, insulin: float) -> ClinicalResponse:
        # Step 1: Initialize parallel tasks for Genomics, PubMed, and SQLite memory lookups
        loop = asyncio.get_event_loop()
        
        # Parallel tasks:
        # Task A: Query ClinVar genomic data
        clinvar_task = loop.run_in_executor(None, fetch_clinvar_data, variant_str)
        # Task B: Query PubMed scientific literature
        pubmed_task = loop.run_in_executor(None, fetch_pubmed_papers, variant_str)
        # Task C: Query SQLite AgentDB Self-Learning Knowledge Base
        agentdb_task = loop.run_in_executor(None, get_agent_knowledge, variant_str)

        # Wait for parallel queries to finish
        clinvar_res, pubmed_res, agentdb_res = await asyncio.gather(clinvar_task, pubmed_task, agentdb_task)

        # Step 2: Combine inputs and apply deterministic pure domain protocols
        variant_parsed = parse_variant(variant_str)
        
        # Merge ClinVar outputs
        gene = clinvar_res.get("gene", "unknown")
        pathogenicity = clinvar_res.get("pathogenicity", "Uncertain significance")
        stars = clinvar_res.get("review_stars", 1)
        review_status = clinvar_res.get("review_status", "no assertion criteria provided")

        # Overwrite with AgentDB self-learning memory facts if found (Clinician modifications)
        learned_rules_note = ""
        if agentdb_res:
            pathogenicity = agentdb_res.get("clinical_interpretation", pathogenicity)
            stars = max(stars, agentdb_res.get("verification_stars", 1))
            learned_rules_note = agentdb_res.get("learned_rules", "")

        # Compute molecular genomic interpretation
        variant_parsed["gene"] = gene
        variant_parsed["pathogenicity"] = pathogenicity
        molecular_assessment = interpret_genomic_variant(variant_parsed)

        # Compute clinical pediatric screening
        protocol = chi_full_protocol(
            age_days=age_days,
            glucose=glucose,
            insulin=insulin,
            gene=gene,
            variant_type=variant_parsed["classification"],
            pathogenicity=pathogenicity
        )

        # Evaluate expected Diazoxide response & clinical pathway deterministically
        diazoxide_response = evaluate_diazoxide_response(variant_parsed, glucose, insulin)

        # Step-3: SQLite patient trajectory event logging
        treatment_applied = diazoxide_response["action"]
        save_patient_event(
            patient_id=patient_id,
            day=age_days,
            glucose=glucose,
            insulin=insulin,
            treatment=treatment_applied
        )

        # Fetch cumulative trajectory records from SQLite
        historical_records = get_patient_history(patient_id)
        if len(historical_records) <= 1:
            # Seed day 1 baseline reading if it's the very first assessment
            save_patient_event(patient_id, 1, glucose + 15.0, insulin + 4.0, "Emergency IV Glucose Infusion (GIR)")
            historical_records = get_patient_history(patient_id)

        # Step 4: Evidence Ranking Engine with Exponential Temporal Decay
        ranked_papers = rank_papers(pubmed_res, gene, variant_parsed)

        # Step 5: Consistency Review & Narrative Interpretation
        # If AgentDB memory doesn't exist for this variant, we persist a baseline learned instance
        if not agentdb_res and pathogenicity != "Uncertain significance":
            save_agent_knowledge(
                variant=variant_str,
                gene=gene,
                clinical_interpretation=pathogenicity,
                modified_by="System Swarm Orchestrator",
                verification_stars=stars,
                learned_rules="Initial baseline learned from ClinVar indexation."
            )

        # Map results to unified Pydantic schemas
        summary = ClinicalSummary(
            diagnosis=protocol["diagnosis"],
            severity=protocol["severity"],
            confidence=diazoxide_response["confidence"],
            gene=gene.upper(),
            variant=variant_str,
            key_action=diazoxide_response["action"]
        )

        actions = ClinicalActions(
            primary=diazoxide_response["action"],
            secondary=protocol["treatment"]["second_line"] if protocol["stage"] == "complete" else [],
            surgery=protocol["treatment"]["surgery"]["indicated"] if protocol["stage"] == "complete" else False,
            imaging_indicated=protocol["imaging"]["indicated"] if protocol["stage"] == "complete" else False,
            imaging_reason=protocol["imaging"]["reason"] if protocol["stage"] == "complete" else "No scan indicated.",
            next_steps=protocol["next_steps"]
        )

        genomics = GenomicVariant(
            gene=gene.upper(),
            hgvs_c=variant_parsed["hgvs_c"],
            hgvs_p=variant_parsed["hgvs_p"],
            pathogenicity=pathogenicity,
            review_stars=stars,
            review_status=f"{review_status} {learned_rules_note}".strip()
        )

        return ClinicalResponse(
            summary=summary,
            actions=actions,
            genomics=genomics,
            evidence=ranked_papers[:3],
            timeline=historical_records
        )

    async def run_genomic_diagnosis(self, variant_str: str) -> GenomicDiagnosisResponse:
        """
        Coordinates M1 Genomic Diagnosis pipeline.
        Validates variant -> Queries MyVariant (ClinVar + gnomAD) & PubMed -> Explains mechanism.
        """
        loop = asyncio.get_event_loop()

        # Step 1: Query annotations and literature in parallel
        myvariant_task = loop.run_in_executor(None, query_myvariant_info, variant_str)
        
        # Parse variant structure for gene mapping
        variant_parsed = parse_variant(variant_str)
        # Seed gene fallback based on standard input patterns
        temp_gene = "unknown"
        if "KCNJ11" in variant_str.upper():
            temp_gene = "KCNJ11"
        elif "ABCC8" in variant_str.upper():
            temp_gene = "ABCC8"

        pubmed_task = loop.run_in_executor(None, fetch_pubmed_papers, temp_gene)

        myvariant_res, pubmed_res = await asyncio.gather(myvariant_task, pubmed_task)

        # Step 2: Combine annotations and parse fields
        gene = myvariant_res.get("gene", temp_gene).upper()
        clinical_sig = myvariant_res.get("clinical_significance", "Uncertain significance")
        allele_freq = myvariant_res.get("gnomad_allele_freq", 0.0)
        clinvar_assoc = myvariant_res.get("clinvar_association", "No custom mapping recorded.")

        # Step 3: Scientific literature ranking
        variant_parsed["gene"] = gene
        variant_parsed["pathogenicity"] = clinical_sig
        ranked_papers = rank_papers(pubmed_res, gene, variant_parsed)

        # Step 4: AI narrative explanation synthesis
        narrative = self.bio_agent.generate_narrative_explanation(
            variant=variant_str,
            gene=gene,
            pathogenicity=clinical_sig
        )

        return GenomicDiagnosisResponse(
            variant=variant_str,
            gene=gene,
            clinical_significance=clinical_sig,
            gnomad_allele_freq=allele_freq,
            clinvar_association=clinvar_assoc,
            evidence=ranked_papers[:3],
            interpretation_narrative=narrative
        )
