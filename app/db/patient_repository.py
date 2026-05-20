import os
import sqlite3
from typing import List
from app.models.clinical_models import PatientHistory

DB_PATH = os.path.join(os.path.dirname(__file__), "patients.db")

def init_db():
    """
    Initializes the local SQLite database for patient history.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
