import pandas as pd
from datetime import date


TODAY = date(2026, 5, 8)


def get_escalation_stage(days_overdue):
    if 1 <= days_overdue <= 7:
        return "Stage 1 — Warm & Friendly"
    elif 8 <= days_overdue <= 14:
        return "Stage 2 — Polite but Firm"
    elif 15 <= days_overdue <= 21:
        return "Stage 3 — Formal & Serious"
    elif 22 <= days_overdue <= 30:
        return "Stage 4 — Stern & Urgent"
    elif days_overdue > 30:
        return "ESCALATION — Flag for Legal"
    else:
        return "Not Yet Overdue"


def calculate_days_overdue(due_date_str):
    due_date = pd.to_datetime(due_date_str).date()
    return (TODAY - due_date).days


def load_and_process_invoices(filepath):
    df = pd.read_csv(filepath)
    df["days_overdue"] = df["due_date"].apply(calculate_days_overdue)
    df["tone_stage"] = df["days_overdue"].apply(get_escalation_stage)
    return df[["invoice_no", "client_name", "days_overdue", "tone_stage"]]


def print_results(results):
    print(f"\n{'='*70}")
    print(f"  INVOICE ESCALATION REPORT — As of {TODAY}")
    print(f"{'='*70}\n")

    for _, row in results.iterrows():
        print(f"  Invoice   : {row['invoice_no']}")
        print(f"  Client    : {row['client_name']}")
        print(f"  Overdue   : {row['days_overdue']} days")
        print(f"  Tone/Stage: {row['tone_stage']}")
        print(f"  {'-'*50}")

    print(f"\n  Total Invoices Processed: {len(results)}\n")


if __name__ == "__main__":
    results = load_and_process_invoices("data/pending_invoices.csv")
    print_results(results)