import os
import sqlite3
from typing import List, Optional
from app.models.clinical_models import PatientHistory

DB_PATH = os.path.join(os.path.dirname(__file__), "patients.db")

def init_db():
    """
    Initializes the local SQLite database for patient history and AgentDB.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ─── 1. Patient history trajectory table ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_history (
            patient_id TEXT,
            day INTEGER,
            glucose REAL,
            insulin REAL,
            treatment TEXT,
            PRIMARY KEY (patient_id, day)
        )
    """)
    # ─── 2. AgentDB Self-Learning Knowledge Base ───
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_knowledge_base (
            variant TEXT PRIMARY KEY,
            gene TEXT,
            clinical_interpretation TEXT,
            modified_by TEXT,
            verification_stars INTEGER,
            learned_rules TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_patient_event(patient_id: str, day: int, glucose: float, insulin: float, treatment: str):
    """
    Persists a daily physiological event for a patient.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO patient_history (patient_id, day, glucose, insulin, treatment)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, day, glucose, insulin, treatment))
    conn.commit()
    conn.close()

def get_patient_history(patient_id: str) -> List[PatientHistory]:
    """
    Retrieves all historic physiological readings for a patient, sorted by day.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT day, glucose, insulin, treatment 
        FROM patient_history 
        WHERE patient_id = ? 
        ORDER BY day ASC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append(PatientHistory(
            day=r[0],
            glucose=r[1],
            insulin=r[2],
            treatment=r[3]
        ))
    return history

def save_agent_knowledge(variant: str, gene: str, clinical_interpretation: str, modified_by: str, verification_stars: int, learned_rules: str):
    """
    Saves or updates self-learned clinical overrides inside the AgentDB table.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO agent_knowledge_base (variant, gene, clinical_interpretation, modified_by, verification_stars, learned_rules)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (variant, gene, clinical_interpretation, modified_by, verification_stars, learned_rules))
    conn.commit()
    conn.close()

def get_agent_knowledge(variant: str) -> Optional[dict]:
    """
    Queries AgentDB for persistent self-learned clinical insights matching the variant.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gene, clinical_interpretation, modified_by, verification_stars, learned_rules 
        FROM agent_knowledge_base 
        WHERE variant = ?
    """, (variant,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "gene": row[0],
            "clinical_interpretation": row[1],
            "modified_by": row[2],
            "verification_stars": row[3],
            "learned_rules": row[4]
        }
    return None
