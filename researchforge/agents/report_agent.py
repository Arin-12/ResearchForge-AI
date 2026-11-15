
from google.adk.agents import LlmAgent
from researchforge.config import get_model_for_agent

report_agent = LlmAgent(
    name="report_agent",
    model=get_model_for_agent("report"),
    description="Writes a concise, evidence-grounded research proposal.",
    instruction="""Research analysis:
{analysis_results}

Write an academic research proposal using these 13 headings:

1. Title
2. Abstract
3. Introduction
4. Literature Review
5. Problem Statement and Research Gap
6. Objectives
7. Research Questions
8. Proposed Methodology
9. Dataset Plan
10. Evaluation Metrics
11. Expected Outcomes
12. Limitations and Risks
13. References

Requirements:
- Keep every section concise and focused.
- Use only paper titles and URLs supplied in the analysis.
- Never invent authors, publication dates, titles, or URLs.
- Mark research gaps as tentative.
- Describe methodology and outcomes as proposed work.
- Do not claim dataset access or verification without evidence.
- Avoid repeating information across sections.
- Preserve all 13 headings.
""",
    output_key="report_draft",
)
