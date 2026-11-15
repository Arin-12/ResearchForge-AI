
import logging
import re
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
MAX_SEARCH_QUERIES = 4

HEADERS = {
    "User-Agent": (
        "ResearchForgeAI/1.0 "
        "(academic research discovery; contact: researchforge@example.com)"
    )
}

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from",
    "in", "into", "is", "of", "on", "or", "the", "to", "using",
    "with", "based", "approach", "system", "study", "research",
    "analysis", "powered", "new", "novel", "method", "methods",
    "model", "models", "deep", "learning", "detection",
}

GENERIC_TERMS = {
    "ai", "artificial", "intelligence", "machine", "learning",
    "deep", "neural", "model", "models", "using", "based",
    "approach", "system", "systems", "detection", "classification",
    "prediction", "analysis", "study", "research", "framework",
    "method", "methods",
}

# Focused expansions for common research concepts.
# These supplement the original query; they do not replace it.
CONCEPT_EXPANSIONS = {
    "ai_generated_text": {
        "triggers": {
            "generated", "generation", "llm", "llms", "gpt",
            "essay", "essays", "authorship", "human",
        },
        "query": "AI-generated text detection and human authorship",
    },
    "image_manipulation": {
        "triggers": {
            "image", "images", "visual", "figure", "figures",
            "manipulated", "manipulation", "forgery", "forensic",
        },
        "query": "image manipulation detection and image forensics",
    },
    "academic_authenticity": {
        "triggers": {
            "academic", "scholarly", "scientific", "research",
            "paper", "papers", "document", "documents",
        },
        "query": "academic document authenticity and content integrity",
    },
    "multimodal": {
        "triggers": {
            "multimodal", "multimodal", "crossmodal",
            "multimodal", "text", "image", "audio",
        },
        "query": "multimodal content authenticity detection",
    },
    "cybersecurity": {
        "triggers": {
            "cybersecurity", "cyber", "threat", "intrusion",
            "malware", "phishing", "ransomware", "network",
        },
        "query": "cyber threat detection and network security",
    },
    "healthcare": {
        "triggers": {
            "healthcare", "medical", "clinical", "patient",
            "disease", "diagnosis", "health",
        },
        "query": "clinical machine learning and medical prediction",
    },
    "fake_news": {
        "triggers": {
            "fake", "news", "misinformation", "disinformation",
            "rumor", "rumour",
        },
        "query": "misinformation detection and information credibility",
    },
}


def _build_http_session():
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

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=5,
        pool_maxsize=5,
    )

    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


HTTP = _build_http_session()


def _get_json(endpoint, *, params, source):
    response = HTTP.get(
        endpoint,
        params=params,
        timeout=(5, TIMEOUT),
    )

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "unknown")
        raise requests.HTTPError(
            f"{source} rate limited the request "
            f"(HTTP 429; Retry-After={retry_after})",
            response=response,
        )

    response.raise_for_status()
    return response.json()


def _tokens(text):
    words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def _clean_abstract(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(unescape(text).split())[:1200]


def _build_search_queries(topic):
    """
    Build a small set of focused queries while preserving the original topic.
    """

    topic = " ".join(topic.split())
    topic_tokens = _tokens(topic)

    queries = [topic]

    # Add concept-specific queries only when topic terms support them.
    for config in CONCEPT_EXPANSIONS.values():
        if topic_tokens.intersection(config["triggers"]):
            queries.append(config["query"])

    # Add useful topic fragments when the topic is long.
    # Split on conjunctions and common linking phrases.
    fragments = re.split(
        r"\s+(?:and|using|with|for|through|based on)\s+",
        topic,
        flags=re.IGNORECASE,
    )

    for fragment in fragments:
        fragment = fragment.strip(" ,.-")
        if len(_tokens(fragment)) >= 2:
            queries.append(fragment)

    # Preserve order and remove duplicate queries.
    unique = []
    seen = set()

    for query in queries:
        key = query.lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(query)

        if len(unique) >= MAX_SEARCH_QUERIES:
            break

    return unique



def _relevance_score(query, title, abstract):
    query_tokens = _tokens(query)
    title_tokens = _tokens(title)
    abstract_tokens = _tokens(abstract)

    if not query_tokens:
        return 0.0, 0

    title_hits = query_tokens.intersection(title_tokens)
    abstract_hits = query_tokens.intersection(abstract_tokens)

    score = (
        2 * len(title_hits) + len(abstract_hits)
    ) / (3 * len(query_tokens))

    return round(min(score, 1.0), 3), len(title_hits | abstract_hits)


def _best_paper_relevance(topic, search_queries, title, abstract):
    """
    Score independently against the original topic and focused queries.
    Return the strongest match instead of combining all query terms.
    """

    candidates = [topic] + search_queries[1:]
    best = (0.0, 0, topic)

    for candidate_query in candidates:
        score, matched_terms = _relevance_score(
            candidate_query,
            title,
            abstract,
        )

        if (score, matched_terms) > (best[0], best[1]):
            best = (score, matched_terms, candidate_query)

    return best



def _make_paper(
    *,
    title,
    authors,
    abstract,
    year,
    url,
    source,
    doi="",
):
    return {
        "title": (title or "").strip(),
        "authors": (authors or [])[:5],
        "summary": _clean_abstract(abstract)[:500],
        "published": str(year or ""),
        "url": url or "",
        "doi": doi or "",
        "source": source,
    }


def _search_arxiv(query):
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
                    authors=[a.name for a in result.authors],
                    abstract=result.summary,
                    year=result.published.year if result.published else "",
                    url=result.entry_id,
                    source="arXiv",
                )
            )

        return papers, "ok"

    except Exception as exc:
        logger.warning("arXiv search failed: %s", exc)
        return [], f"failed: {type(exc).__name__}: {exc}"


def _search_semantic_scholar(query):
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": PER_SOURCE_LIMIT,
        "fields": "title,authors,year,abstract,url,externalIds",
    }

    try:
        payload = _get_json(
            endpoint,
            params=params,
            source="Semantic Scholar",
        )

        papers = []

        for item in payload.get("data", []):
            external_ids = item.get("externalIds") or {}
            doi = external_ids.get("DOI", "")

            url = item.get("url") or (
                f"https://doi.org/{doi}" if doi else ""
            )

            if not url or not item.get("title"):
                continue

            papers.append(
                _make_paper(
                    title=item.get("title"),
                    authors=[
                        a.get("name", "")
                        for a in item.get("authors", [])
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
        logger.warning("Semantic Scholar search failed: %s", exc)
        return [], f"failed: {type(exc).__name__}: {exc}"


def _search_crossref(query):
    endpoint = "https://api.crossref.org/works"

    params = {
        "query": query,
        "rows": PER_SOURCE_LIMIT,
        "select": "DOI,title,author,published,URL,abstract,type",
    }

    try:
        payload = _get_json(
            endpoint,
            params=params,
            source="Crossref",
        )

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
                    part for part in (
                        author.get("given", ""),
                        author.get("family", ""),
                    ) if part
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
        logger.warning("Crossref search failed: %s", exc)
        return [], f"failed: {type(exc).__name__}: {exc}"


def _dedup_key(paper):
    doi = (paper.get("doi") or "").lower().strip()
    if doi:
        return f"doi:{doi}"

    url = (paper.get("url") or "").lower().strip()

    if "arxiv.org/abs/" in url:
        arxiv_id = url.split("/abs/")[-1]
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        return f"arxiv:{arxiv_id}"

    title = re.sub(
        r"[^a-z0-9]+",
        " ",
        (paper.get("title") or "").lower(),
    ).strip()

    return f"title:{title}"


def _merge_paper(existing, incoming):
    if incoming["source"] != existing["source"]:
        if incoming["source"] not in existing["also_found_by"]:
            existing["also_found_by"].append(incoming["source"])

    # Prefer records with richer metadata.
    for field in ("summary", "doi", "published", "url", "authors"):
        if not existing.get(field) and incoming.get(field):
            existing[field] = incoming[field]

    return existing


def search_research_papers(query):
    """
    Search arXiv, Semantic Scholar and Crossref using focused queries.
    Returns deduplicated, relevance-ranked records.
    """

    if not isinstance(query, str) or not query.strip():
        return {
            "query": query or "",
            "papers_found": 0,
            "papers": [],
            "source_status": {},
            "message": "A non-empty research topic is required.",
        }

    query = " ".join(query.split())
    search_queries = _build_search_queries(query)

    logger.info("Paper search queries: %s", search_queries)

    providers = {
        "arXiv": _search_arxiv,
        "Semantic Scholar": _search_semantic_scholar,
        "Crossref": _search_crossref,
    }

    candidates = []
    source_status = {}

    for source, search_function in providers.items():
        source_status[source] = {}

        # Avoid repeatedly hitting a provider after a rate-limit response.
        provider_rate_limited = False

        for search_query in search_queries:
            if provider_rate_limited:
                source_status[source][search_query] = (
                    "skipped_after_rate_limit"
                )
                continue

            records, status = search_function(search_query)
            source_status[source][search_query] = status

            candidates.extend(records)

            if "429" in status or "rate limit" in status.lower():
                provider_rate_limited = True

    # Use the original topic and focused query terms for ranking.
    ranking_terms = _tokens(query)

    for search_query in search_queries[1:]:
        ranking_terms.update(_tokens(search_query))


    ranked = []

    for paper in candidates:
        title = paper.get("title", "")
        summary = paper.get("summary", "")

        score, matched_terms, matched_query = _best_paper_relevance(
            query,
            search_queries,
            title,
            summary,
        )

        # Avoid retaining papers supported by only one matching term.
        if matched_terms < 2 or score < 0.15:
            continue

        paper["relevance_score"] = score
        paper["matched_topic_terms"] = matched_terms
        paper["matched_search_query"] = matched_query
        paper["also_found_by"] = []

        ranked.append(paper)


    unique = {}

    for paper in ranked:
        key = _dedup_key(paper)

        if key not in unique:
            unique[key] = paper
        else:
            _merge_paper(unique[key], paper)

    final_papers = sorted(
        unique.values(),
        key=lambda item: (
            item.get("relevance_score", 0),
            item.get("matched_topic_terms", 0),
            bool(item.get("summary")),
            bool(item.get("doi")),
        ),
        reverse=True,
    )[:FINAL_LIMIT]

    return {
        "query": query,
        "search_queries_used": search_queries,
        "papers_found": len(final_papers),
        "papers": final_papers,
        "source_status": source_status,
        "filter_note": (
            "Relevance scores are keyword-overlap estimates across the "
            "original topic and focused queries. They do not establish "
            "semantic relevance, peer-review status or scientific quality."
        ),
        "fallback_note": (
            "Each provider is queried independently. A provider that "
            "returns a rate-limit response is skipped for remaining "
            "queries; results from other providers are retained."
        ),
    }
