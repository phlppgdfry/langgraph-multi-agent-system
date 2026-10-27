# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## 🛡️ Reporting a Vulnerability

We take the security of autonomous agent systems seriously. If you discover a security vulnerability or credential leak risk:

1. **Do not create a public GitHub issue.**
2. Email details and steps to reproduce to: **philippe.godfroy@hotmail.com**.
3. We will acknowledge receipt within 48 hours and coordinate a timely fix.

---

## 🔒 Credential & API Key Safety

- All API keys (`LANGCHAIN_API_KEY`, `OPENAI_API_KEY`, etc.) must strictly reside in `.env` or system environment variables.
- `.env`, `.env.local`, and `*.db` are strictly excluded via `.gitignore` to prevent secret leakage.
- Never commit credentials to version control.
