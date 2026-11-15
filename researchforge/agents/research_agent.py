
from google.adk.agents import LlmAgent
from researchforge.config import get_model_for_agent

from researchforge.tools.paper_search import search_research_papers
from researchforge.tools.dataset_discovery import (
    discover_datasets,
    suggest_dataset_search_links,
)
from researchforge.tools.citation_validation import (
    validate_paper_urls,
)

research_agent = LlmAgent(
    name="research_agent",
    model=get_model_for_agent("research"),
    description="Finds concise, traceable research evidence.",
    instruction="""Research procedure:

1. Call search_research_papers exactly once with the user's research topic.
2. Read the returned papers list and source_status for arXiv,
   Semantic Scholar, and Crossref.
3. Use only papers returned by the search tool.
4. Prioritize papers with higher relevance scores, but remember that
   the score is a keyword-overlap estimate, not proof of relevance.
5. Do not invent missing authors, publication years, abstracts, DOIs,
   or URLs.
6. If a source fails, report that source's failure. Do not claim that
   all three sources were searched successfully.
7. If no sufficiently relevant papers are returned, state that the
   search found insufficient relevant results. Do not fill the report
   with unrelated papers.
8. Call discover_datasets once with the research topic. Treat returned
   records as catalog metadata only, not as downloaded or quality-verified data.
9. Call suggest_dataset_search_links only if discover_datasets returns
   no useful records; do not duplicate the links otherwise.
10. Call validate_paper_urls once, passing both the paper URLs and the
    corresponding paper records so DOI/title/year metadata can be compared.
11. Distinguish URL reachability and metadata matching from verification
    of full text or scientific claims.

Return:
- Topic
- Search Sources and Status
- Relevant Papers (maximum 8)
  - Exact title
  - Authors, if available
  - Publication year, if available
  - Source
  - Relevance score
  - DOI, if available
  - URL
  - Short evidence-based summary, if available
- Dataset Catalog Matches (source, dataset name, URL, available metadata)
- Dataset Search Links
- Citation/URL/DOI Metadata Checks
- Evidence Limitations
""",
    tools=[
        search_research_papers,
        discover_datasets,
        suggest_dataset_search_links,
        validate_paper_urls,
    ],
    output_key="research_results",
)
