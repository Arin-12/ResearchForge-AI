
from google.adk.agents import LlmAgent
from researchforge.config import get_model_for_agent

analysis_agent = LlmAgent(
    name="analysis_agent",
    model=get_model_for_agent("analysis"),
    description="Develops a concise, evidence-grounded research direction.",
    instruction="""Analyze the research evidence:
{research_results}

Return concise bullet points under these headings:

1. Literature Review
2. Common Themes and Limitations
3. Tentative Research Gap
4. Objectives and Research Questions
5. Proposed Methodology
6. Evaluation Metrics
7. Dataset Plan
8. Expected Outcomes and Risks

Requirements:
- Do not reproduce full abstracts or the complete evidence list.
- Cite only supplied paper titles and URLs.
- Separate established evidence from hypotheses and proposed work.
- Do not claim that datasets were downloaded or verified.
- A limited search cannot establish that no prior research exists.
- If evidence is insufficient, state the uncertainty.
- Prefer useful, specific points over lengthy explanations.
""",
    output_key="analysis_results",
)
