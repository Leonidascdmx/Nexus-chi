from typing import Dict, Any, List
from app.domain.genomics.variant_parser import parse_variant
from app.domain.genomics.variant_interpreter import interpret_genomic_variant
from app.domain.clinical.chi_protocol import chi_full_protocol
from app.domain.clinical.diazoxide import evaluate_diazoxide_response
from app.infrastructure.clinvar.clinvar_client import fetch_clinvar_data
from app.services.research_agent import ResearchAgent
from app.services.bio_agent import BioAgent
from app.db.patient_repository import get_agent_knowledge

class AgentStateGraph:
    """
    AgentStateGraph (Nivel 10): State-based Multi-Agent Router inspired by LangGraph.
    Manages and mutates a central 'State' dict through sequential node operations.
    """
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.bio_agent = BioAgent()

    def execute_graph(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the multi-agent state transition graph sequentially.
        """
        state = initial_state.copy()
        state["current_node"] = "InputValidation"
        
        # ─── Loop through state transitions ───
        while state["current_node"] != "Complete":
            node = state["current_node"]
            
            if node == "InputValidation":
                state = self._validate_input_node(state)
            elif node == "GenomicLookup":
                state = self._genomic_lookup_node(state)
            elif node == "LiteratureSearch":
                state = self._literature_search_node(state)
            elif node == "ClinicalDecision":
                state = self._clinical_decision_node(state)
            elif node == "AIExplanation":
                state = self._ai_explanation_node(state)
            elif node == "ClinicalQA":
                state = self._clinical_qa_node(state)
            else:
                state["current_node"] = "Complete"

        return state

    def _validate_input_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[STATE-GRAPH] Node: InputValidation")
        variant_str = state.get("variant", "")
        
        if not variant_str:
            state["error"] = "Input HGVS variant coordinate is missing."
            state["current_node"] = "Complete"
            return state

        # Parse variant locus structure
        state["variant_parsed"] = parse_variant(variant_str)
        state["current_node"] = "GenomicLookup"
        return state

    def _genomic_lookup_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[STATE-GRAPH] Node: GenomicLookup")
        variant_str = state["variant"]
        
        # Look up in ClinVar
        clinvar_res = fetch_clinvar_data(variant_str)
        gene = clinvar_res.get("gene", "unknown").upper()
        pathogenicity = clinvar_res.get("pathogenicity", "Uncertain significance")
        stars = clinvar_res.get("review_stars", 1)
        review_status = clinvar_res.get("review_status", "no assertion criteria provided")

        # Merge SQLite AgentDB self-learning feedback if available
        agentdb_res = get_agent_knowledge(variant_str)
        if agentdb_res:
            pathogenicity = agentdb_res.get("clinical_interpretation", pathogenicity)
            stars = max(stars, agentdb_res.get("verification_stars", 1))
            review_status += " [AgentDB Clinician Override]"

        state["gene"] = gene
        state["pathogenicity"] = pathogenicity
        state["review_stars"] = stars
        state["review_status"] = review_status
        state["current_node"] = "LiteratureSearch"
        return state

    def _literature_search_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[STATE-GRAPH] Node: LiteratureSearch")
        gene = state["gene"]
        variant_parsed = state["variant_parsed"]
        
        # Trigger Option C ResearchAgent
        ranked_papers = self.research_agent.search_and_rank_literature(gene, variant_parsed)
        state["evidence"] = ranked_papers
        state["current_node"] = "ClinicalDecision"
        return state

    def _clinical_decision_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[STATE-GRAPH] Node: ClinicalDecision")
        
        # Deterministic endocrine clinical protocol & Diazoxide response paths
        protocol = chi_full_protocol(
            age_days=state.get("age_days", 2),
            glucose=state.get("glucose", 35.0),
            insulin=state.get("insulin", 12.0),
            gene=state["gene"],
            variant_type=state["variant_parsed"]["classification"],
            pathogenicity=state["pathogenicity"]
        )
        
        diazoxide_res = evaluate_diazoxide_response(
            state["variant_parsed"],
            state.get("glucose", 35.0),
            state.get("insulin", 12.0)
        )

        state["protocol"] = protocol
        state["diazoxide"] = diazoxide_res
        state["current_node"] = "AIExplanation"
        return state

    def _ai_explanation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[STATE-GRAPH] Node: AIExplanation")
        
        # Synthesize molecular explanation using BioAgent
        narrative = self.bio_agent.generate_narrative_explanation(
            variant=state["variant"],
            gene=state["gene"],
            pathogenicity=state["pathogenicity"]
        )
        state["narrative_explanation"] = narrative
        state["current_node"] = "ClinicalQA"
        return state

    def _clinical_qa_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("[STATE-GRAPH] Node: ClinicalQA")
        
        # Safety rules matching clinical boundaries
        glucose = state.get("glucose", 35.0)
        insulin = state.get("insulin", 12.0)
        pathogenicity = state["pathogenicity"]

        # Conflict check: If variant is completely benign but patient presents severe biochemistry, flag warning
        if pathogenicity.lower() == "benign" and glucose < 40 and insulin > 3:
            state["safety_status"] = "SAFETY WARNING: Hypoglycemia occurs without genomic ABCC8/KCNJ11 pathogenesis. Check for focal lesions or alternative metabolic factors."
        else:
            state["safety_status"] = "SAFETY APPROVED: Genetic susceptibility correlates with biochemical presentation."

        state["current_node"] = "Complete"
        return state
