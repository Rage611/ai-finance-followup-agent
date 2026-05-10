import os
import sqlite3
from datetime import datetime


# Configuration

LOGS_DIRECTORY  = "logs"
DATABASE_PATH   = os.path.join(LOGS_DIRECTORY, "audit_trail.db")


# Database Setup

def setup_database():
    """
    Ensures the logs directory exists and initialises the SQLite audit
    database. Creates the email_audit_log table if it does not already exist.
    """
    os.makedirs(LOGS_DIRECTORY, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor     = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_audit_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT    NOT NULL,
            invoice_no    TEXT    NOT NULL,
            client_name   TEXT    NOT NULL,
            tone_stage    TEXT    NOT NULL,
            email_body    TEXT,
            status        TEXT    NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print(f"  [Database] Audit trail ready at: {DATABASE_PATH}")


# Audit Logging

def log_interaction(invoice, email_body, status):
    """
    Inserts a single interaction record into the audit trail database.

    Args:
        invoice    : An InvoiceContext dataclass containing invoice details.
        email_body : The generated email text, or None if skipped.
        status     : A string describing the outcome (e.g. 'Simulated Send').
    """
    connection = sqlite3.connect(DATABASE_PATH)
    cursor     = connection.cursor()

    cursor.execute("""
        INSERT INTO email_audit_log
            (timestamp, invoice_no, client_name, tone_stage, email_body, status)
        VALUES
            (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        invoice.invoice_no,
        invoice.client_name,
        invoice.tone_stage,
        email_body,
        status,
    ))

    connection.commit()
    connection.close()