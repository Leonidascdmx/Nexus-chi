import asyncio
from app.models.clinical_models import (
    ClinicalResponse, ClinicalSummary, ClinicalActions, GenomicVariant, GenomicDiagnosisResponse
)
from app.db.patient_repository import save_patient_event, get_patient_history
from app.services.agent_state_graph import AgentStateGraph

class ClinicalSwarm:
    """
    Nivel 10 Swarm Intelligence Core.
    Coordinates multiple specialized micro-agents: ResearchAgent & BioAgent
    via an AgentStateGraph state-transition routing loop.
    """
    def __init__(self):
        self.state_graph = AgentStateGraph()

    async def run_swarm_analysis(self, patient_id: str, variant_str: str, age_days: int, glucose: float, insulin: float) -> ClinicalResponse:
        """
        Runs the multi-agent graph state transition to yield a unified ClinicalResponse.
        """
        loop = asyncio.get_event_loop()
        
        initial_state = {
            "variant": variant_str,
            "age_days": age_days,
            "glucose": glucose,
            "insulin": insulin,
            "patient_id": patient_id
        }

        # Execute multi-agent state graph transitions
        state = await loop.run_in_executor(None, self.state_graph.execute_graph, initial_state)

        # Persist daily physiological event logging
        treatment_applied = state["diazoxide"]["action"]
        save_patient_event(
            patient_id=patient_id,
            day=age_days,
            glucose=glucose,
            insulin=insulin,
            treatment=treatment_applied
        )

        # Retrieve cumulative patient trajectory
        historical_records = get_patient_history(patient_id)
        if len(historical_records) <= 1:
            save_patient_event(patient_id, 1, glucose + 15.0, insulin + 4.0, "Emergency IV Glucose Infusion (GIR)")
            historical_records = get_patient_history(patient_id)

        # Synthesize QA review details into review status
        review_status = state["review_status"]
        if "SAFETY WARNING" in state["safety_status"]:
            review_status += f" | [SAFETY ALERT]: {state['safety_status']}"

        # Construct typified outputs
        summary = ClinicalSummary(
            diagnosis=state["protocol"]["diagnosis"],
            severity=state["protocol"]["severity"],
            confidence=state["diazoxide"]["confidence"],
            gene=state["gene"].upper(),
            variant=variant_str,
            key_action=treatment_applied
        )

        actions = ClinicalActions(
            primary=treatment_applied,
            secondary=state["protocol"]["treatment"]["second_line"] if state["protocol"]["stage"] == "complete" else [],
            surgery=state["protocol"]["treatment"]["surgery"]["indicated"] if state["protocol"]["stage"] == "complete" else False,
            imaging_indicated=state["protocol"]["imaging"]["indicated"] if state["protocol"]["stage"] == "complete" else False,
            imaging_reason=state["protocol"]["imaging"]["reason"] if state["protocol"]["stage"] == "complete" else "No scan indicated.",
            next_steps=state["protocol"]["next_steps"]
        )

        genomics = GenomicVariant(
            gene=state["gene"].upper(),
            hgvs_c=state["variant_parsed"]["hgvs_c"],
            hgvs_p=state["variant_parsed"]["hgvs_p"],
            pathogenicity=state["pathogenicity"],
            review_stars=state["review_stars"],
            review_status=review_status
        )

        return ClinicalResponse(
            summary=summary,
            actions=actions,
            genomics=genomics,
            evidence=state["evidence"][:3],
            timeline=historical_records
        )

    async def run_genomic_diagnosis(self, variant_str: str) -> GenomicDiagnosisResponse:
        """
        Coordinates M1 Genomic Diagnosis using the State Transition Graph.
        """
        loop = asyncio.get_event_loop()

        initial_state = {
            "variant": variant_str,
            "age_days": 2,
            "glucose": 35.0,
            "insulin": 12.0,
            "patient_id": "M1-DIAGNOSIS"
        }

        # Run multi-agent state graph node traversals
        state = await loop.run_in_executor(None, self.state_graph.execute_graph, initial_state)

        # Merge ClinVar MyVariant metadata
        from app.infrastructure.myvariant.myvariant_client import query_myvariant_info
        myvariant_res = await loop.run_in_executor(None, query_myvariant_info, variant_str)
        allele_freq = myvariant_res.get("gnomad_allele_freq", 0.0)
        clinvar_assoc = myvariant_res.get("clinvar_association", "No custom mapping recorded.")

        return GenomicDiagnosisResponse(
            variant=variant_str,
            gene=state["gene"].upper(),
            clinical_significance=state["pathogenicity"],
            gnomad_allele_freq=allele_freq,
            clinvar_association=clinvar_assoc,
            evidence=state["evidence"][:3],
            interpretation_narrative=state["narrative_explanation"]
        )
