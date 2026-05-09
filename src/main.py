from dotenv import load_dotenv
load_dotenv()

import sys
import pandas as pd

from data_ingestion import load_and_process_invoices
from email_service  import setup_database, log_interaction
from llm_engine     import generate_follow_up_email, InvoiceContext


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INVOICES_FILE        = "data/pending_invoices.csv"
LEGAL_ESCALATION_TAG = "ESCALATION — Flag for Legal"


# ---------------------------------------------------------------------------
# Routing Logic
# ---------------------------------------------------------------------------

def process_invoice(invoice):
    """
    Applies the critical routing logic for a single invoice:

    - If the tone stage is a legal escalation, the LLM is bypassed entirely.
      The invoice is flagged for human review with no email generated.
    - For all other stages, the LLM generates a personalised follow-up email,
      which is printed to the terminal and logged to the audit trail.

    Args:
        invoice : An InvoiceContext dataclass for the current invoice.
    """
    print(f"\n  {'─'*60}")
    print(f"  Processing : {invoice.invoice_no} — {invoice.client_name}")
    print(f"  Tone Stage : {invoice.tone_stage}")

    if invoice.tone_stage == LEGAL_ESCALATION_TAG:
        print(f"  ⚠️  ESCALATION DETECTED — Bypassing LLM. Flagging for human review.")
        log_interaction(invoice, email_body=None, status="Flagged for Human Review")
        return

    email_body = generate_follow_up_email(invoice)

    print(f"\n  ✅ Email Generated Successfully\n")
    print(f"  {'·'*60}")
    print(email_body)
    print(f"  {'·'*60}")

    log_interaction(invoice, email_body=email_body, status="Simulated Send")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    print(f"\n{'='*64}")
    print(f"  FINANCE AI AGENT — Master Controller")
    print(f"  Phase 3: Audit Trail & Email Dispatch (Dry Run)")
    print(f"{'='*64}")

    # Phase 1 — Load and process all invoices
    invoice_dataframe = load_and_process_invoices(INVOICES_FILE)

    # Phase 3 — Initialise the audit trail database
    print()
    setup_database()

    total_invoices  = len(invoice_dataframe)
    simulated_count = 0
    flagged_count   = 0

    # Phase 2 + 3 — Loop, route, generate, and log
    for _, row in invoice_dataframe.iterrows():

        invoice = InvoiceContext(
            invoice_no   = row["invoice_no"],
            client_name  = row["client_name"],
            amount       = row["amount"],
            due_date     = row["due_date"],
            days_overdue = row["days_overdue"],
            tone_stage   = row["tone_stage"],
        )

        process_invoice(invoice)

        if invoice.tone_stage == LEGAL_ESCALATION_TAG:
            flagged_count  += 1
        else:
            simulated_count += 1

    # Summary
    print(f"\n\n{'='*64}")
    print(f"  RUN COMPLETE — Summary")
    print(f"{'='*64}")
    print(f"  Total Invoices Processed : {total_invoices}")
    print(f"  Emails Simulated         : {simulated_count}")
    print(f"  Flagged for Human Review : {flagged_count}")
    print(f"  Audit log saved to       : logs/audit_trail.db")
    print(f"{'='*64}\n")


if __name__ == "__main__":
    main()