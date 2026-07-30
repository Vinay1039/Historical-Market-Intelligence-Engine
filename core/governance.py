"""
===============================================================================
 HMIE Research Governance Engine (core/governance.py)
 Enforces the Canonical Result Policy (v2.1 Governance Layer Freeze)

 Dual-Hash System:
   - EXECUTION_HASH : SHA256(study_id + methodology_version + dataset_version + parameters)
   - RESULT_HASH    : SHA256(summary_metrics_json)
===============================================================================
"""

import hashlib
import json
import logging

logger = logging.getLogger(__name__)

def generate_hash(data_dict: dict) -> str:
    """Generate deterministic SHA256 hash of a dictionary."""
    serialized = json.dumps(data_dict, sort_keys=True)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

def register_execution(
    conn,
    study_id: str,
    study_name: str,
    methodology_version: str,
    dataset_version: str,
    parameters: dict,
    summary_metrics: dict,
    statistical_limitations: list = None,
    is_canonical: bool = True,
    git_commit: str = "a4b7f92e8c10d3"  # Immutable commit reference
):
    """
    Registers an experiment execution in STAGING.RESEARCH_EXECUTIONS.
    Computes both EXECUTION_HASH and RESULT_HASH.
    If is_canonical=True, automatically archives previous runs for this study_id.
    """
    cursor = conn.cursor()
    
    cursor.execute("SELECT NVL(MAX(EXECUTION_ID), 0) + 1 FROM STAGING.RESEARCH_EXECUTIONS")
    exec_id = int(cursor.fetchone()[0])
    
    exec_payload = {
        "study_id": study_id,
        "methodology_version": methodology_version,
        "dataset_version": dataset_version,
        "parameters": parameters
    }
    execution_hash = generate_hash(exec_payload)
    result_hash = generate_hash(summary_metrics)
    
    metrics_json = json.dumps(summary_metrics, sort_keys=True)
    limitations_json = json.dumps(statistical_limitations or [], sort_keys=True)
    
    supersedes_id = None
    
    if is_canonical:
        cursor.execute("""
            SELECT EXECUTION_ID FROM STAGING.RESEARCH_EXECUTIONS
            WHERE STUDY_ID = :1 AND CANONICAL_FLAG = 1
        """, [study_id])
        row = cursor.fetchone()
        if row:
            supersedes_id = int(row[0])
            cursor.execute("""
                UPDATE STAGING.RESEARCH_EXECUTIONS
                SET CANONICAL_FLAG = 0
                WHERE EXECUTION_ID = :1
            """, [supersedes_id])
            logger.info(f"   [Governance] Exec ID {supersedes_id} marked ARCHIVED (superseded by {exec_id})")

    cursor.execute("""
        INSERT INTO STAGING.RESEARCH_EXECUTIONS (
            EXECUTION_ID, STUDY_ID, STUDY_NAME, METHODOLOGY_VERSION,
            DATASET_VERSION, GIT_COMMIT, CANONICAL_FLAG,
            EXECUTION_HASH, RESULT_HASH, SUMMARY_METRICS_JSON,
            LIMITATIONS_JSON, SUPERSEDES_EXEC_ID
        ) VALUES (
            :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12
        )
    """, [
        exec_id, study_id, study_name, methodology_version,
        dataset_version, git_commit, 1 if is_canonical else 0,
        execution_hash, result_hash, metrics_json,
        limitations_json, supersedes_id
    ])
    
    conn.commit()
    cursor.close()
    
    logger.info(f" ✓ [Governance] Exec ID {exec_id} [{study_id}] Registered | ExecHash: {execution_hash[:10]} | ResultHash: {result_hash[:10]}")
    return exec_id
