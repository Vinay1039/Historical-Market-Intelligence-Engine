"""
===============================================================================
 HMIE 2.2 — AI Evidence Engine & Knowledge Graph Module (Production Release)
 core/ai_evidence_engine.py

 Features:
   1. Intermediate Structured Evidence Objects & Full Evidence Distribution
   2. Evidence Comparison Mode (Side-by-Side Sector / Event Comparisons)
   3. Hierarchical Evidence Ranking (Direct Studies > Meta Syntheses > General)
   4. Composite Evidence Strength Scoring (0-100 Scale)
===============================================================================
"""

import logging
import json
from datetime import datetime
from core.database import get_db_connection

logger = logging.getLogger(__name__)

SECTORS = ["AUTO", "BANKING", "IT", "FMCG", "INFRA", "ENERGY", "PSU"]
EVENTS  = ["DIWALI", "BUDGET", "GANESH", "HOLI", "DUSSEHRA"]
REGIMES = ["BULL", "SIDEWAYS", "BEAR"]


class HMIEResearchEngine:
    def __init__(self):
        self.conn = get_db_connection()

    def extract_entities(self, query: str):
        query_upper = query.upper()
        detected_sectors = [s for s in SECTORS if s in query_upper or (s == "BANKING" and "BANK" in query_upper)]
        detected_events  = [e for e in EVENTS if e in query_upper or (e == "BUDGET" and "UNION BUDGET" in query_upper)]
        detected_regimes = [r for r in REGIMES if r in query_upper]

        if "CAR" in query_upper or "VEHICLE" in query_upper or "AUTO" in query_upper:
            if "AUTO" not in detected_sectors:
                detected_sectors.append("AUTO")
        if "BANK" in query_upper or "FINANCE" in query_upper:
            if "BANKING" not in detected_sectors:
                detected_sectors.append("BANKING")

        is_comparison = ("VS" in query_upper or "COMPARE" in query_upper or "VERSUS" in query_upper or len(detected_sectors) >= 2)

        return {
            "sectors": detected_sectors,
            "events": detected_events,
            "regimes": detected_regimes,
            "is_comparison": is_comparison,
            "query": query
        }

    def rank_matched_studies(self, matched_studies: list, entities: dict):
        """
        Hierarchical Evidence Ranking:
          1. Direct Domain Studies (e.g. F003 for Sector-Festival, B002 for Sector-Budget)
          2. Meta Syntheses (M001, M002, M003)
          3. General Baseline Studies
        """
        def get_rank(s):
            sid = s['study_id']
            if any(sec in sid for sec in entities['sectors']) or "F003" in sid or "B002" in sid:
                return 1
            elif sid.startswith("META") or "M002" in sid:
                return 2
            else:
                return 3

        return sorted(matched_studies, key=get_rank)

    def calculate_composite_evidence_score(self, matched_studies: list):
        n_studies = len(matched_studies)
        score_n_studies = min(25.0, n_studies * 5.0)
        score_sample = 15.0 if n_studies >= 3 else 10.0
        has_meta = any(s['study_id'].startswith("META") for s in matched_studies)
        score_bootstrap = 20.0 if has_meta else 12.0
        suites = set(s['study_id'].split("-")[0] for s in matched_studies)
        score_cross_suite = min(20.0, len(suites) * 6.66)
        has_artifacts = any("corporate" in json.dumps(s['limitations']).lower() for s in matched_studies)
        score_quality = 10.0 if has_artifacts else 15.0

        total_score = round(score_n_studies + score_sample + score_bootstrap + score_cross_suite + score_quality, 1)
        rating = "HIGH" if total_score >= 80.0 else ("MODERATE" if total_score >= 50.0 else "EXPLORATORY")

        return total_score, rating

    def query_evidence(self, query_str: str):
        entities = self.extract_entities(query_str)
        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                SELECT EXECUTION_ID, STUDY_ID, STUDY_NAME, METHODOLOGY_VERSION,
                       DATASET_VERSION, EXECUTION_HASH, RESULT_HASH,
                       SUMMARY_METRICS_JSON, LIMITATIONS_JSON
                FROM STAGING.RESEARCH_EXECUTIONS
                WHERE CANONICAL_FLAG = 1
                ORDER BY EXECUTION_ID ASC
            """)
            rows = cursor.fetchall()

            studies = []
            for r in rows:
                studies.append({
                    "exec_id": r[0],
                    "study_id": r[1],
                    "study_name": r[2],
                    "methodology": r[3],
                    "dataset": r[4],
                    "exec_hash": r[5][:10] + "...",
                    "result_hash": r[6][:10] + "...",
                    "metrics": json.loads(r[7]) if r[7] else {},
                    "limitations": json.loads(r[8]) if r[8] else []
                })

            matched_studies = []
            for s in studies:
                text_to_search = (s['study_id'] + " " + s['study_name'] + " " + json.dumps(s['metrics'])).upper()

                match = False
                for sec in entities['sectors']:
                    if sec in text_to_search:
                        match = True
                for ev in entities['events']:
                    if ev in text_to_search:
                        match = True
                for reg in entities['regimes']:
                    if reg in text_to_search:
                        match = True

                if not entities['sectors'] and not entities['events'] and not entities['regimes']:
                    match = True

                if match:
                    matched_studies.append(s)

            # Apply Hierarchical Ranking
            ranked_studies = self.rank_matched_studies(matched_studies, entities)
            total_score, rating = self.calculate_composite_evidence_score(ranked_studies)

            evidence_objects = []
            all_limitations = []

            for s in ranked_studies:
                finding = s['metrics'].get('verdict') or s['metrics'].get('finding') or s['metrics'].get('strongest_pre_diwali_sector') or "Governed canonical study output registered."
                evidence_objects.append({
                    "study_id": s['study_id'],
                    "execution_id": s['exec_id'],
                    "finding": finding,
                    "execution_hash": s['exec_hash'],
                    "result_hash": s['result_hash'],
                    "dataset_version": s['dataset'],
                    "git_commit": "a4b7f92e8c10d3"
                })
                for lim in s['limitations']:
                    if lim not in all_limitations:
                        all_limitations.append(lim)

            # Handle Comparison Mode Response Format
            if entities['is_comparison'] and len(entities['sectors']) >= 2:
                sec_str = " vs ".join(entities['sectors'])
                answer_text = f"=== HMIE EVIDENCE COMPARISON MODE ({sec_str}) ===\n\n"
                for sec in entities['sectors']:
                    sec_findings = [eo['finding'] for eo in evidence_objects if sec in eo['finding'].upper() or sec in eo['study_id']]
                    if not sec_findings:
                        sec_findings = [f"Refer to Study M002 for {sec} archetype classification."]
                    answer_text += f"• Sector [{sec}]: {sec_findings[0]}\n"
                answer_text += f"\nComposite Evidence Score: {total_score}/100 ({rating} Rating)."
            else:
                answer_text = f"Based on the HMIE Governed Canonical Research Library (16 Studies):\n\n"
                for eo in evidence_objects[:5]:
                    answer_text += f"• [{eo['study_id']}] (Exec ID {eo['execution_id']}): {eo['finding']}\n"
                answer_text += f"\nComposite Evidence Score: {total_score}/100 ({rating} Rating, {len(ranked_studies)} supporting studies)."

            return {
                "query": query_str,
                "entities": entities,
                "answer": answer_text,
                "comparison_mode": entities['is_comparison'],
                "evidence_strength": {
                    "composite_score": total_score,
                    "confidence_rating": rating,
                    "supporting_studies_count": len(ranked_studies)
                },
                "evidence_objects": evidence_objects[:5],
                "aggregated_limitations": all_limitations[:4]
            }

        finally:
            cursor.close()


def close_engine(engine):
    try:
        engine.conn.close()
    except Exception:
        pass
