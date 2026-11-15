
from google.adk.agents import SequentialAgent

from researchforge.agents.research_agent import research_agent
from researchforge.agents.analysis_agent import analysis_agent
from researchforge.agents.report_agent import report_agent
from researchforge.agents.reviewer_agent import reviewer_agent


root_agent = SequentialAgent(
    name="researchforge_workflow",
    description="Research → Analysis → Report → Review pipeline",
    sub_agents=[
        research_agent,
        analysis_agent,
        report_agent,
        reviewer_agent,
    ],
)
