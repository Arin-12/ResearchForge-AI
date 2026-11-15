
from google.adk.agents import LlmAgent
from researchforge.config import get_model_for_agent
from researchforge.tools.citation_validation import validate_report_structure

reviewer_agent = LlmAgent(
    name="reviewer_agent",
    model=get_model_for_agent("reviewer"),
    description="Reviews research proposals for grounding and citation integrity.",
    instruction="""Original research evidence:
{research_results}

Research analysis:
{analysis_results}

Proposal draft:
{report_draft}

Review and correct the complete proposal.

Check:
- Whether claims are supported by the original research evidence.
- Whether references match the supplied titles and URLs.
- Whether research gaps are presented as tentative.
- Whether dataset search links are incorrectly described as verified datasets.
- Whether hypotheses are incorrectly presented as proven results.
- Whether all 13 required headings are present.
- Whether references contain entries and are drawn only from the original evidence.
- Whether dataset catalog matches are distinguished from downloaded/validated data.

Before finalizing, call validate_report_structure on the proposal draft.
Use its result to repair missing headings or an empty References section.
This is a structural check only, not proof of citation accuracy.

Requirements:
- Make only necessary corrections.
- Never invent references or supporting evidence.
- Preserve all 13 headings.
- Keep the corrected proposal concise.
- End with "Review Notes" listing limitations and items requiring human verification.
- Return the complete corrected report, not review comments alone.
""",
    tools=[validate_report_structure],
    output_key="final_report",
)
