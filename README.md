# Finance AI Agent — Automated Invoice Follow-Up 🤖

Most finance teams spend hours every week writing the same follow-up emails. Same message, different client name, slightly different tone depending on how late the payment is. It's repetitive, it's manual, and honestly it's the kind of work that shouldn't require a human in 2026.

This project automates that entire workflow end-to-end.

---

## What it does ✅

The agent reads a CSV of pending invoices, figures out how overdue each one is, picks the right tone, writes a personalised email using Gemini 2.5, and logs everything to an audit trail. If an invoice is over 30 days overdue, it skips the AI entirely and flags it for a human to review — because legal-risk decisions shouldn't be automated.

That last part is intentional. One of the things I thought hard about while building this is where the human stays in the loop.

---

## The escalation logic 📊

Not every overdue invoice should get the same email. A client who's 3 days late gets a gentle nudge. A client who's 28 days late gets something very different. The agent maps each invoice to a stage automatically:

| Days Overdue    | Stage         | Tone |

| 1–7             | Stage 1       | Warm & Friendly — assumes it's just an oversight |
| 8–14            | Stage 2       | Polite but Firm — references the previous reminder |
| 15–21           | Stage 3       | Formal & Serious — direct, requests immediate action |
| 22–30           | Stage 4       | Stern & Urgent — makes consequences clear |
| 30+             | ⚠️ Escalation | LLM bypassed — flagged for human review |

The LLM receives the stage as part of its prompt and adjusts its language accordingly. Every email comes out different — different wording, different urgency, specific to that client and invoice number.

---

## How it's structured 🗂️

The project is split into three phases, each in its own file:

**data_ingestion.py** handles reading the CSV, calculating days overdue, and assigning the escalation stage. Nothing else.

**llm_engine.py** takes an invoice's details and talks to Gemini 2.5. It uses a fixed system prompt to set the agent's persona and a dynamic user prompt that injects the actual invoice data. The two-layer prompt design keeps output consistent while still making each email feel specific.

**email_service.py + main.py** tie everything together. Main runs the loop, applies the routing logic, and decides whether to call the LLM or bypass it. Everything — sent, skipped, or flagged — gets written to a SQLite audit log.

    finance-ai-agent/
    ├── data/
    │   └── pending_invoices.csv
    ├── logs/
    │   └── audit_trail.db        (auto-created on first run)
    └── src/
        ├── data_ingestion.py
        ├── llm_engine.py
        ├── email_service.py
        └── main.py

---

## Running it 🚀

Clone the repo, install dependencies, add your Gemini API key to a .env file, then:

    python src/main.py

It'll process each invoice, print the generated emails to the terminal, and save everything to the audit log.

---

## Stack 🛠️

Python, Gemini 2.5, Pandas, SQLite, python-dotenv.

---

## What's next 🗺️

A few things I want to add when I pick this back up:

- Plug in SendGrid to actually send the emails instead of simulating
- Build a small Streamlit dashboard to review flagged escalations before a human acts on them
- Add a scheduler so it runs automatically every morning without being triggered manually

---

Built this to get hands-on with AI agent design in a real business context — specifically around the parts that matter in production: prompt control, routing logic, audit trails, and knowing when not to use AI. 💡

## Security & Risk Mitigation 🛡️

Because this handles financial data and automated communication, I built in specific guardrails:

- Prompt Injection: By using LangChain, the system instructions are strictly separated from the 
  dynamic user data. Malicious inputs in the CSV cannot override the agent's persona.
- API Key Leakage: Credentials are kept entirely out of source control using a local .env file 
  and .gitignore.
- Accidental Sends: The system runs in a pure "dry-run" mode. There is no SMTP server 
  connected, meaning there is zero risk of accidentally emailing real clients during testing.
- Legal/Hallucination Risk: The 30+ day hardcoded escalation cap guarantees the AI cannot go    
  rogue and generate unauthorized legal threats.