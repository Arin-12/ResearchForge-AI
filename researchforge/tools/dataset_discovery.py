
"""Discover and relevance-filter public dataset catalog records."""

import logging
import re
from urllib.parse import quote_plus

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

TIMEOUT = 12
MAX_RECORDS_PER_SOURCE = 5
MAX_NAME_LENGTH = 150

HEADERS = {
    "User-Agent": "ResearchForgeAI/1.0 (dataset discovery)"
}

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from",
    "in", "into", "is", "of", "on", "or", "the", "to", "using",
    "with", "based", "approach", "system", "study", "research",
    "analysis", "powered", "new", "novel", "model", "models",
    "detection", "deep", "learning", "framework", "method",
    "methods", "data", "dataset",
}

GENERIC_TERMS = {
    "ai", "artificial", "intelligence", "machine", "learning",
    "deep", "neural", "model", "models", "approach", "system",
    "systems", "detection", "classification", "prediction",
    "analysis", "study", "research", "framework", "method",
    "methods", "data", "dataset", "content",
}

HTTP = requests.Session()

retry = Retry(
    total=2,
    connect=2,
    read=1,
    status=2,
    backoff_factor=1,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({"GET"}),
    respect_retry_after_header=True,
    raise_on_status=False,
)

adapter = HTTPAdapter(max_retries=retry)
HTTP.mount("https://", adapter)
HTTP.mount("http://", adapter)
HTTP.headers.update(HEADERS)


def _safe_text(value, max_length=200):
    if value is None or isinstance(value, (dict, list)):
        return None

    value = str(value).strip()

    return value[:max_length] if value else None


def _tokens(text):
    words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())

    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def _topic_terms(topic):
    return _tokens(topic) - GENERIC_TERMS


def _dataset_relevance(topic, searchable_text):
    """
    Transparent lexical relevance estimate.
    It is not a semantic model or a quality assessment.
    """

    topic_terms = _topic_terms(topic)
    dataset_terms = _tokens(searchable_text)

    if not topic_terms:
        return 0.0, 0, []

    matched = sorted(topic_terms.intersection(dataset_terms))
    score = len(matched) / len(topic_terms)

    return round(score, 3), len(matched), matched



def _dataset_queries(topic):
    """
    Generate focused dataset searches for relevant research modalities.
    """

    topic_tokens = _tokens(topic)

    queries = [topic]

    if topic_tokens.intersection({
        "generated", "generation", "llm", "essay",
        "authorship", "human", "text",
    }):
        queries.append(
            "AI generated text detection dataset"
        )

    if topic_tokens.intersection({
        "image", "images", "visual", "figure",
        "manipulation", "manipulated", "forgery",
    }):
        queries.append(
            "image manipulation and forgery detection dataset"
        )

    if topic_tokens.intersection({
        "academic", "scholarly", "scientific",
        "paper", "papers", "document", "documents",
    }):
        queries.append(
            "academic document authenticity and PDF dataset"
        )

    if topic_tokens.intersection({
        "multimodal", "document", "documents",
        "pdf", "layout", "structure",
    }):
        queries.append(
            "multimodal document understanding and layout dataset"
        )

    unique = []
    seen = set()

    for query in queries:
        key = query.lower().strip()

        if key and key not in seen:
            seen.add(key)
            unique.append(query)

        if len(unique) >= 5:
            break

    return unique



def _search_huggingface(query):
    try:
        response = HTTP.get(
            "https://huggingface.co/api/datasets",
            params={
                "search": query,
                "limit": MAX_RECORDS_PER_SOURCE,
                "sort": "downloads",
                "direction": -1,
            },
            timeout=(5, TIMEOUT),
        )

        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list):
            return [], "invalid_api_response"

        records = []

        for item in payload:
            if not isinstance(item, dict):
                continue

            dataset_id = _safe_text(
                item.get("id"),
                MAX_NAME_LENGTH,
            )

            if not dataset_id:
                continue

            card_data = item.get("cardData")
            card_data = card_data if isinstance(card_data, dict) else {}

            tags = item.get("tags")
            if not isinstance(tags, list):
                tags = []

            description = (
                card_data.get("description")
                or card_data.get("task_categories")
                or ""
            )

            searchable_text = " ".join(
                str(value)
                for value in [
                    dataset_id,
                    description,
                    " ".join(str(tag) for tag in tags),
                ]
                if value
            )

            license_name = _safe_text(
                card_data.get("license"),
                100,
            )

            records.append({
                "name": dataset_id,
                "source": "Hugging Face",
                "url": f"https://huggingface.co/datasets/{dataset_id}",
                "description": _safe_text(description, 300),
                "tags": tags[:15],
                "downloads": (
                    item.get("downloads")
                    if isinstance(item.get("downloads"), int)
                    else None
                ),
                "likes": (
                    item.get("likes")
                    if isinstance(item.get("likes"), int)
                    else None
                ),
                "last_modified": _safe_text(
                    item.get("lastModified"),
                    30,
                ),
                "license": license_name,
                "_searchable_text": searchable_text,
                "record_type": "catalog_record",

                "_searchable_text": searchable_text,
                "_search_queries": [query],
                "record_type": "catalog_record",
            })

        return records, "ok"

    except (requests.RequestException, ValueError, TypeError) as exc:
        logger.warning("Hugging Face search failed: %s", exc)
        return [], f"failed: {type(exc).__name__}: {exc}"


def _search_openml(query):
    try:
        response = HTTP.get(
            "https://www.openml.org/api/v1/json/data/list",
            params={
                "search": query,
                "limit": MAX_RECORDS_PER_SOURCE,
                "status": "active",
            },
            timeout=(5, TIMEOUT),
        )

        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, dict):
            return [], "invalid_api_response"

        data_section = payload.get("data", {})

        if not isinstance(data_section, dict):
            return [], "invalid_api_response"

        raw = data_section.get("dataset", [])

        if isinstance(raw, dict):
            raw = [raw]

        if not isinstance(raw, list):
            return [], "invalid_dataset_records"

        records = []

        for item in raw:
            if not isinstance(item, dict):
                continue

            dataset_id = _safe_text(item.get("did"), 30)
            name = _safe_text(item.get("name"), MAX_NAME_LENGTH)

            if not dataset_id or not name:
                continue

            searchable_text = " ".join(
                str(value)
                for value in [
                    name,
                    item.get("format", ""),
                    item.get("default_target_attribute", ""),
                ]
                if value
            )

            records.append({
                "name": name,
                "source": "OpenML",
                "dataset_id": dataset_id,
                "url": f"https://www.openml.org/d/{dataset_id}",
                "version": _safe_text(item.get("version"), 30),
                "format": _safe_text(item.get("format"), 50),
                "default_target_attribute": _safe_text(
                    item.get("default_target_attribute"),
                    100,
                ),
                "_searchable_text": searchable_text,
                "record_type": "catalog_record",

                "_searchable_text": searchable_text,
                "_search_queries": [query],
                "record_type": "catalog_record",
            })

        return records, "ok"

    except (
        requests.RequestException,
        ValueError,
        TypeError,
        AttributeError,
    ) as exc:
        logger.warning("OpenML search failed: %s", exc)
        return [], f"failed: {type(exc).__name__}: {exc}"



def _merge_records(records):
    merged = {}

    for record in records:
        key = (
            record.get("source", ""),
            record.get("dataset_id") or record.get("name", "").lower(),
        )

        if key not in merged:
            merged[key] = record
            continue

        existing = merged[key]

        for field in (
            "description",
            "license",
            "tags",
            "downloads",
            "likes",
        ):
            if not existing.get(field) and record.get(field):
                existing[field] = record[field]

        existing_queries = existing.setdefault("_search_queries", [])

        for query in record.get("_search_queries", []):
            if query not in existing_queries:
                existing_queries.append(query)

    return list(merged.values())



def discover_datasets(topic, limit=2):
    """
    Search Hugging Face and OpenML and return relevance-filtered
    catalog records. Dataset files are not downloaded.
    """

    if not isinstance(topic, str) or not topic.strip():
        return {
            "query": "",
            "datasets": [],
            "dataset_count": 0,
            "source_status": {},
            "message": "A non-empty topic is required.",
        }

    topic = " ".join(topic.split())[:200]

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 2

    limit = max(1, min(limit, MAX_RECORDS_PER_SOURCE))

    queries = _dataset_queries(topic)

    all_hf = []
    all_openml = []

    source_status = {
        "Hugging Face": {},
        "OpenML": {},
    }

    for search_query in queries:
        hf_records, hf_status = _search_huggingface(search_query)
        openml_records, openml_status = _search_openml(search_query)

        all_hf.extend(hf_records)
        all_openml.extend(openml_records)

        source_status["Hugging Face"][search_query] = hf_status
        source_status["OpenML"][search_query] = openml_status

    all_records = _merge_records(all_hf + all_openml)


    relevant = []

    for record in all_records:
        searchable_text = record.pop("_searchable_text", "")
        matched_queries = record.pop("_search_queries", [])

        # Evaluate against the original topic and the queries
        # that actually discovered this dataset.
        candidate_queries = [topic] + matched_queries

        best_score = 0.0
        best_count = 0
        best_terms = []
        best_query = topic

        for candidate_query in candidate_queries:
            score, matched_count, matched_terms = _dataset_relevance(
                candidate_query,
                searchable_text,
            )

            if (score, matched_count) > (best_score, best_count):
                best_score = score
                best_count = matched_count
                best_terms = matched_terms
                best_query = candidate_query

        if best_count < 2 or best_score < 0.20:
            continue

        record["relevance_score"] = best_score
        record["matched_topic_terms"] = best_terms
        record["matched_search_query"] = best_query

        record["relevance_label"] = (
            "strong_candidate" if best_score >= 0.40
            else "partial_candidate"
        )

        record["note"] = (
            "Catalog match based on available metadata. "
            "Inspect the dataset card, schema, labels, license "
            "and actual samples before deciding suitability."
        )

        relevant.append(record)

    relevant.sort(
        key=lambda item: (
            item["relevance_score"],
            item.get("downloads") or 0,
            item.get("likes") or 0,
        ),
        reverse=True,
    )

    # Keep results balanced across providers.
    hf_results = [
        item for item in relevant
        if item["source"] == "Hugging Face"
    ][:limit]

    openml_results = [
        item for item in relevant
        if item["source"] == "OpenML"
    ][:limit]

    datasets = hf_results + openml_results

    return {
        "query": topic,
        "search_queries_used": queries,
        "datasets": datasets,
        "dataset_count": len(datasets),
        "source_status": {
            source: (
                "ok" if any(status == "ok" for status in statuses.values())
                else "failed"
            )
            for source, statuses in source_status.items()
        },
        "source_query_status": source_status,
        "message": (
            "No relevant dataset catalog records were identified. "
            "Try broader or modality-specific searches."
            if not datasets
            else "Relevant catalog candidates found. Manual verification is required."
        ),
        "limitations": (
            "Relevance is estimated from names, tags and available metadata. "
            "A catalog match does not establish data quality, label validity, "
            "license compatibility, accessibility or suitability. "
            "Dataset files are not downloaded or inspected."
        ),
    }


def suggest_dataset_search_links(topic):
    """Generate external discovery links, not verified dataset records."""

    if not isinstance(topic, str) or not topic.strip():
        return []

    q = quote_plus(topic.strip()[:200])

    return [
        {
            "name": "Kaggle Datasets",
            "search_url": (
                f"https://www.kaggle.com/datasets?search={q}"
            ),
            "note": "Search link only; review license and quality.",
        },
        {
            "name": "UCI Repository",
            "search_url": (
                f"https://archive.ics.uci.edu/search?query={q}"
            ),
            "note": "Search link only; review documentation and terms.",
        },
        {
            "name": "OpenML",
            "search_url": (
                "https://www.openml.org/search?type=data"
                f"&sort=runs&id=&status=active&name={q}"
            ),
            "note": "Search link only; inspect task, features and license.",
        },
        {
            "name": "Hugging Face Datasets",
            "search_url": (
                f"https://huggingface.co/datasets?search={q}"
            ),
            "note": "Search link only; inspect dataset card and license.",
        },
    ]
