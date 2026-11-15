# ResearchForge AI — Google ADK + Groq Cloud

Modular VS Code project based on the uploaded notebook. Google ADK handles agent orchestration; Groq Cloud serves `openai/gpt-oss-20b` through ADK's LiteLLM connector.

## Four agents
1. Research: arXiv search, dataset repository search links, paper URL checks.
2. Analysis: literature review, tentative gap, objectives, method and evaluation plan.
3. Report: structured research proposal/report.
4. Reviewer: checks unsupported claims, references, dataset claims, and missing sections.

## Setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and set your own `GROQ_API_KEY`. Then:
```powershell
python main.py
```
Enter a research topic. The reviewed report is printed and saved to `outputs/`.

## Provider note
This is **Groq Cloud**, not xAI's Grok API. Model is configured as `groq/openai/gpt-oss-20b`. Do not commit `.env`.

## Structure
```text
main.py
researchforge/
  config.py logging_config.py models.py agent.py workflow.py
  agents/ research_agent.py analysis_agent.py report_agent.py reviewer_agent.py
  tools/ paper_search.py dataset_discovery.py citation_validation.py
  utils/output.py
```

## Limitations
Dataset search links are discovery starting points, not verified datasets. URL reachability does not prove a citation supports a claim. The reviewer is a quality-control pass, not a correctness guarantee. End-to-end execution requires a valid Groq API key, model access, quota, and network access.
