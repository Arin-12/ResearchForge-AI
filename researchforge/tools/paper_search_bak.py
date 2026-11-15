import logging
import re
import time
from html import unescape

import arxiv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from researchforge.config import MAX_PAPERS

logger = logging.getLogger(__name__)

TIMEOUT = 12
PER_SOURCE_LIMIT = 5
FINAL_LIMIT = MAX_PAPERS

HEADERS = {
    "User-Agent": "ResearchForgeAI/1.0 (academic research discovery; contact: researchforge@example.com)"
}


def _build_http_session() -> requests.Session:
    """Create a reusable session with bounded retries for transient API errors."""
    retry = Retry(
        total=3,
        connect=3,
        read=2,
        status=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=5, pool_maxsize=5)
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


HTTP = _build_http_session()


def _get_json(endpoint: str, *, params: dict, source: str) -> dict:
    """GET JSON with shared retry/backoff and explicit HTTP error reporting."""
    response = HTTP.get(endpoint, params=params, timeout=(5, TIMEOUT))
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "unknown")
        raise requests.HTTPError(
            f"{source} rate limited the request (HTTP 429; Retry-After={retry_after})",
            response=response,
        )
    response.raise_for_status()
    return response.json()

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from",
    "in", "into", "is", "of", "on", "or", "the", "to", "using",
    "with", "based", "approach", "system", "study", "research",
    "analysis", "powered", "new", "novel"
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
    return {word for word in words if len(word) > 2 and word not in STOP_WORDS}


def _clean_abstract(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(unescape(text).split())[:1200]



GENERIC_TERMS = {
    "ai", "artificial", "intelligence", "machine", "learning",
    "deep", "neural", "model", "models", "using", "based",
    "approach", "system", "systems", "detection", "classification",
    "prediction", "analysis", "study", "research"
}

DOMAIN_ANCHORS = {
    "cybersecurity": {
        "cyber", "cybersecurity", "threat", "intrusion", "malware",
        "phishing", "ransomware", "network", "ids", "attack",
        "vulnerability", "botnet"
    },
    "healthcare": {
        "healthcare", "medical", "clinical", "patient", "disease",
        "diagnosis", "medicine", "hospital"
    },
    "fake news": {
        "fake", "news", "misinformation", "disinformation",
        "misleading", "rumor", "rumour"
    }
}


def _relevance_score(query: str, title: str, abstract: str):
    query_tokens = _tokens(query)
    title_tokens = _tokens(title)
    abstract_tokens = _tokens(abstract)

    if not query_tokens:
        return 0.0, 0

    title_hits = query_tokens.intersection(title_tokens)
    abstract_hits = query_tokens.intersection(abstract_tokens)
    all_hits = title_hits | abstract_hits

    score = (
        2 * len(title_hits) + len(abstract_hits)
    ) / (3 * len(query_tokens))

    return round(min(score, 1.0), 3), len(all_hits)



def _passes_domain_filter(query: str, title: str, abstract: str) -> bool:
    query_lower = query.lower()
    text = f"{title} {abstract}".lower()

    domain_groups = {
        "cybersecurity": [
            "cybersecurity", "cyber threat", "intrusion detection",
            "malware", "phishing", "ransomware", "network security",
            "cyber attack", "botnet", "vulnerability"
        ],
        "healthcare": [
            "healthcare", "medical", "clinical", "patient",
            "diagnosis", "disease", "medical question answering"
        ],
        "fake news": [
            "fake news", "misinformation", "disinformation",
            "rumor", "rumour"
        ]
    }

    for domain, keywords in domain_groups.items():
        if domain in query_lower or (
            domain == "cybersecurity" and "cyber" in query_lower
        ):
            return any(keyword in text for keyword in keywords)

    topic_terms = _tokens(query) - GENERIC_TERMS

    if not topic_terms:
        return True

    return bool(topic_terms.intersection(_tokens(title)))




def _make_paper(
    *,
    title: str,
    authors: list[str],
    abstract: str,
    year: str,
    url: str,
    source: str,
    doi: str = "",
) -> dict:
    return {
        "title": title.strip(),
        "authors": authors[:5],
        "summary": _clean_abstract(abstract)[:500],
        "published": str(year or ""),
        "url": url,
        "doi": doi,
        "source": source,
    }


def _search_arxiv(query: str) -> tuple[list[dict], str]:
    try:
        client = arxiv.Client(
            page_size=PER_SOURCE_LIMIT,
            delay_seconds=3.0,
            num_retries=2,
        )
        search = arxiv.Search(
            query=query,
            max_results=PER_SOURCE_LIMIT,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = []
        for result in client.results(search):
            papers.append(
                _make_paper(
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    year=result.published.year if result.published else "",
                    url=result.entry_id,
                    source="arXiv",
                )
            )
        return papers, "ok"

    except Exception as exc:
        logger.warning("arXiv search failed: %s", exc)
        return [], f"{type(exc).__name__}: {exc}"


def _search_semantic_scholar(query: str) -> tuple[list[dict], str]:
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": PER_SOURCE_LIMIT,
        "fields": "title,authors,year,abstract,url,externalIds",
    }

    try:
        payload = _get_json(endpoint, params=params, source="Semantic Scholar")

        papers = []
        for item in payload.get("data", []):
            external_ids = item.get("externalIds") or {}
            doi = external_ids.get("DOI", "")
            url = item.get("url") or (
                f"https://doi.org/{doi}" if doi else ""
            )

            if not url:
                continue

            papers.append(
                _make_paper(
                    title=item.get("title", ""),
                    authors=[
                        author.get("name", "")
                        for author in item.get("authors", [])
                    ],
                    abstract=item.get("abstract", ""),
                    year=item.get("year", ""),
                    url=url,
                    source="Semantic Scholar",
                    doi=doi,
                )
            )

        return papers, "ok"

    except Exception as exc:
        logger.warning("Semantic Scholar search failed after retries: %s", exc)
        # Other providers are still queried by search_research_papers.
        return [], f"failed_after_retries: {type(exc).__name__}: {exc}"


def _search_crossref(query: str) -> tuple[list[dict], str]:
    endpoint = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": PER_SOURCE_LIMIT,
        "select": "DOI,title,author,published,URL,abstract,type",
    }

    try:
        payload = _get_json(endpoint, params=params, source="Crossref")
        items = payload.get("message", {}).get("items", [])
        papers = []

        for item in items:
            titles = item.get("title") or []
            title = titles[0] if titles else ""
            doi = item.get("DOI", "")
            url = item.get("URL") or (
                f"https://doi.org/{doi}" if doi else ""
            )

            date_parts = (
                item.get("published", {}).get("date-parts", [[]])[0]
            )
            year = date_parts[0] if date_parts else ""

            authors = []
            for author in item.get("author", []):
                name = " ".join(
                    part for part in [
                        author.get("given", ""),
                        author.get("family", ""),
                    ] if part
                )
                if name:
                    authors.append(name)

            if not title or not url:
                continue

            papers.append(
                _make_paper(
                    title=title,
                    authors=authors,
                    abstract=item.get("abstract", ""),
                    year=year,
                    url=url,
                    source="Crossref",
                    doi=doi,
                )
            )

        return papers, "ok"

    except Exception as exc:
        logger.warning("Crossref search failed after retries: %s", exc)
        return [], f"failed_after_retries: {type(exc).__name__}: {exc}"


def _dedup_key(paper: dict) -> str:
    doi = (paper.get("doi") or "").lower().strip()
    if doi:
        return f"doi:{doi}"

    url = (paper.get("url") or "").lower().strip()
    if "arxiv.org/abs/" in url:
        return "arxiv:" + url.split("/abs/")[-1].split("v")[0]

    title = re.sub(
        r"[^a-z0-9]+", " ",
        (paper.get("title") or "").lower()
    ).strip()
    return f"title:{title}"


def search_research_papers(query: str) -> dict:
    """
    Search arXiv, Semantic Scholar, and Crossref.
    Returns deduplicated papers ranked by a transparent keyword score.
    """
    if not query or not query.strip():
        return {
            "query": query,
            "papers": [],
            "source_status": {},
            "message": "A non-empty research topic is required.",
        }

    query = query.strip()

    # Query providers independently: a failure or 429 from one provider
    # must never prevent results from the other providers being returned.
    arxiv_papers, arxiv_status = _search_arxiv(query)
    semantic_papers, semantic_status = _search_semantic_scholar(query)
    crossref_papers, crossref_status = _search_crossref(query)

    candidates = arxiv_papers + semantic_papers + crossref_papers

    ranked = []
    for paper in candidates:
        score, matched_terms = _relevance_score(
            query, paper["title"], paper["summary"]
        )

        # Avoid accepting papers that match only one generic topic word.
        if matched_terms < 2 or score < 0.30:
            continue

        if not _passes_domain_filter(
            query,
            paper["title"],
            paper["summary"]
        ):
            continue

        paper["relevance_score"] = score
        paper["matched_topic_terms"] = matched_terms
        ranked.append(paper)

    # Merge duplicate records while preserving source provenance.
    unique = {}

    for paper in ranked:
        key = _dedup_key(paper)

        if key not in unique:
            paper["also_found_by"] = []
            unique[key] = paper
            continue

        existing = unique[key]

        if paper["source"] not in existing["also_found_by"]:
            existing["also_found_by"].append(paper["source"])

        for field in ["summary", "doi", "published", "url"]:
            if not existing.get(field) and paper.get(field):
                existing[field] = paper[field]

        if not existing.get("authors") and paper.get("authors"):
            existing["authors"] = paper["authors"]

    final_papers = sorted(
        unique.values(),
        key=lambda item: (
            item["relevance_score"],
            bool(item.get("summary")),
            bool(item.get("doi")),
        ),
        reverse=True,
    )[:FINAL_LIMIT]

    return {
        "query": query,
        "papers_found": len(final_papers),
        "papers": final_papers,

        "source_status": {
            source: (
                "ok" if any(status == "ok" for status in statuses.values())
                else "failed"
            )
            for source, statuses in source_status.items()
        },

        "source_query_status": source_status,

        "filter_note": (
            "Relevance scores are keyword-overlap estimates, not "
            "semantic judgments or assessments of paper quality."
        ),
        "fallback_note": (
            "Providers are queried independently. If one provider fails, "
            "results from successful providers are retained; this is "
            "provider-level fault isolation, not a guarantee of equivalent coverage."
        ),
    }