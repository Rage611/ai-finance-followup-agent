import os
from dotenv import load_dotenv; load_dotenv()
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


# Configuring

GEMINI_MODEL = "gemini-1.5-flash"
PAYMENT_BASE_URL = "https://payments.yourcompany.com/invoices"


# Data Structure

@dataclass
class InvoiceContext:
    """Holds all invoice details required to generate a follow-up email."""
    invoice_no:   str
    client_name:  str
    amount:       float
    due_date:     str
    days_overdue: int
    tone_stage:   str


# Prompt Templates

SYSTEM_PROMPT = """
You are a senior Finance Agent at a professional services company.
Your responsibility is to send payment follow-up emails to clients who have outstanding invoices.

Your behaviour rules:
- You always write in a tone that matches the escalation stage you are given.
- You never send a generic or templated-sounding email. Every email must feel personal and specific to the client and invoice.
- You always include the exact invoice number, amount owed, due date, and days overdue inside the email body.
- You always embed the payment link naturally into the email — never paste it as a raw URL at the end.
- You never threaten legal action unless the tone stage explicitly says "Flag for Legal".
- You sign off as: The Finance Team, YourCompany.
- You output only the email body. No subject line. No explanations. No extra commentary.
""".strip()


def build_user_prompt(invoice: InvoiceContext, payment_link: str) -> str:
    """Constructs the dynamic user prompt with all invoice-specific details."""

    return f"""
Generate a follow-up payment email using the following details:

CLIENT NAME    : {invoice.client_name}
INVOICE NUMBER : {invoice.invoice_no}
AMOUNT DUE     : ${invoice.amount:,.2f}
DUE DATE       : {invoice.due_date}
DAYS OVERDUE   : {invoice.days_overdue} days
PAYMENT LINK   : {payment_link}

TONE/ESCALATION STAGE: {invoice.tone_stage}

Tone guidance per stage:
- Stage 1 — Warm & Friendly     : Light, polite, assumes it is an oversight. Keep it short and encouraging.
- Stage 2 — Polite but Firm     : Friendly but clear that action is needed. Reference the previous reminder.
- Stage 3 — Formal & Serious    : Professional and direct. Express concern about the delay. Request immediate action.
- Stage 4 — Stern & Urgent      : Firm and serious. Communicate urgency and consequences of continued non-payment.
- ESCALATION — Flag for Legal   : Strictly formal. State that the account is being reviewed for legal escalation if payment is not received immediately.

Write the email now. Address it directly to {invoice.client_name}. Do not include a subject line.
""".strip()


# Core Engine

def generate_follow_up_email(invoice: InvoiceContext) -> str:
    """
    Connects to the Anthropic Claude API via LangChain and generates
    a personalised follow-up payment email for the given invoice.

    Args:
        invoice: An InvoiceContext dataclass containing all invoice details.

    Returns:
        A string containing the fully generated follow-up email body.
    """

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4,
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )

    payment_link = f"{PAYMENT_BASE_URL}/{invoice.invoice_no}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=build_user_prompt(invoice, payment_link)),
    ]

    response = llm.invoke(messages)

    return response.content


# Entry Point — Testing All 5 Invoices from Phase 1


if __name__ == "__main__":

    test_invoices = [
        InvoiceContext("INV-2026-001", "Acme Corp",          45000.00,  "2026-05-04",  4,  "Stage 1 — Warm & Friendly"),
        InvoiceContext("INV-2026-002", "Global Tech",         12500.00,  "2026-04-27", 11,  "Stage 2 — Polite but Firm"),
        InvoiceContext("INV-2026-003", "Stark Industries",    89000.00,  "2026-04-20", 18,  "Stage 3 — Formal & Serious"),
        InvoiceContext("INV-2026-004", "Wayne Enterprises",  250000.00,  "2026-04-12", 26,  "Stage 4 — Stern & Urgent"),
        InvoiceContext("INV-2026-005", "Cyberdyne Systems",    5600.00,  "2026-03-15", 54,  "ESCALATION — Flag for Legal"),
    ]

    for invoice in test_invoices:
        print(f"\n{'='*70}")
        print(f"  Generating email for {invoice.invoice_no} — {invoice.client_name}")
        print(f"  Tone: {invoice.tone_stage}")
        print(f"{'='*70}\n")

        email_body = generate_follow_up_email(invoice)

        print(email_body)
        print()