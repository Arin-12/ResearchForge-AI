"""Deterministic checks for paper URL and DOI metadata.

These checks verify bibliographic metadata and URL accessibility only; they
cannot establish that a paper's scientific claims are true.
"""
import logging
import re
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)
TIMEOUT = 8
HEADERS = {"User-Agent": "ResearchForgeAI/1.0 (bibliographic metadata validation)"}
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def _normalize_title(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def _crossref_metadata(doi: str) -> tuple[dict | None, str]:
    if not DOI_PATTERN.match((doi or "").strip()):
        return None, "missing_or_invalid_doi"
    try:
        response = requests.get(
            f"https://api.crossref.org/works/{doi.strip()}",
            timeout=TIMEOUT,
            headers=HEADERS,
        )
        if response.status_code == 404:
            return None, "doi_not_found_in_crossref"
        response.raise_for_status()
        return response.json().get("message", {}), "verified_in_crossref"
    except requests.RequestException as exc:
        logger.warning("Crossref DOI lookup failed for %s: %s", doi, exc)
        return None, f"crossref_lookup_error:{type(exc).__name__}"
    except (ValueError, AttributeError) as exc:
        return None, f"invalid_crossref_response:{type(exc).__name__}"


def _extract_year(metadata: dict) -> str:
    for key in ("published-print", "published-online", "published", "created"):
        date_parts = metadata.get(key, {}).get("date-parts") or []
        if date_parts and date_parts[0]:
            return str(date_parts[0][0])
    return ""


def validate_paper_urls(urls: list[str] | None = None,
                        papers: list[dict] | None = None) -> dict:
    """Check URL reachability and, where DOI exists, Crossref metadata.

    Backward-compatible with the original ``validate_paper_urls(urls)`` call.
    Pass ``papers`` to additionally compare title, year and author metadata.
    """
    paper_items = papers or []
    if not urls:
        urls = [p.get("url", "") for p in paper_items]
    url_to_paper = {p.get("url", ""): p for p in paper_items if p.get("url")}

    results = []
    seen_urls = set()
    for raw_url in (urls or [])[:8]:
        url = (raw_url or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            results.append({"url": url, "reachable": False, "status": "invalid_url"})
            continue

        result = {"url": url, "reachable": False}
        try:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers=HEADERS)
            result.update({
                "reachable": response.status_code < 400,
                "status_code": response.status_code,
                "final_url": response.url,
            })
        except requests.RequestException as exc:
            logger.warning("URL validation failed for %s: %s", url, exc)
            result["status"] = type(exc).__name__

        paper = url_to_paper.get(url, {})
        doi = (paper.get("doi") or "").strip()
        if doi:
            metadata, doi_status = _crossref_metadata(doi)
            result["doi"] = doi
            result["doi_status"] = doi_status
            if metadata:
                crossref_titles = metadata.get("title") or []
                crossref_title = crossref_titles[0] if crossref_titles else ""
                supplied_title = paper.get("title", "")
                title_match = (
                    _normalize_title(supplied_title) == _normalize_title(crossref_title)
                    if supplied_title and crossref_title else None
                )
                crossref_year = _extract_year(metadata)
                supplied_year = str(paper.get("published") or "")
                year_match = (
                    supplied_year[:4] == crossref_year[:4]
                    if supplied_year and crossref_year else None
                )
                result.update({
                    "crossref_title": crossref_title,
                    "title_match": title_match,
                    "crossref_year": crossref_year,
                    "year_match": year_match,
                    "crossref_authors": len(metadata.get("author") or []),
                })
        else:
            result["doi_status"] = "not_supplied"
        results.append(result)

    return {
        "checked": len(results),
        "results": results,
        "limitations": "URL reachability and Crossref metadata matching do not validate full text, peer-review status, or scientific claims.",
    }



def validate_report_structure(report_text: str) -> dict:
    """Check required proposal sections and a populated References section."""

    headings = [
        "Title",
        "Abstract",
        "Introduction",
        "Literature Review",
        "Problem Statement and Research Gap",
        "Objectives",
        "Research Questions",
        "Proposed Methodology",
        "Dataset Plan",
        "Evaluation Metrics",
        "Expected Outcomes",
        "Limitations and Risks",
        "References",
    ]

    def normalize_heading(line: str) -> str:
        line = line.strip()

        # Remove Markdown heading markers.
        line = re.sub(r"^#{1,6}\s*", "", line)

        # Remove bold and italic formatting.
        line = line.replace("*", "").replace("_", "")

        # Remove section numbering: 1. Title, 2) Abstract, etc.
        line = re.sub(r"^\d+\s*[.)-]\s*", "", line)

        # Normalize whitespace and case.
        return " ".join(line.split()).strip().lower()

    text = report_text or ""
    lines = text.splitlines()

    normalized_lines = [
        normalize_heading(line)
        for line in lines
    ]

    normalized_headings = {
        heading.lower(): heading
        for heading in headings
    }

    # Match required headings.
    present = {}

    for heading in headings:
        target = heading.lower()

        present[heading] = any(
            line == target or line.startswith(target + ":")
            for line in normalized_lines
        )

    # Find References section.
    reference_index = next(
        (
            i for i, line in enumerate(normalized_lines)
            if line == "references"
        ),
        None,
    )

    references_content = []

    if reference_index is not None:
        for line in normalized_lines[reference_index + 1:]:

            if not line or line == "---":
                continue

            # Stop at reviewer notes.
            if line.startswith("review notes"):
                break

            # Stop if another recognized major heading appears.
            if line in normalized_headings:
                break

            references_content.append(line)

    missing = [
        heading
        for heading, found in present.items()
        if not found
    ]

    return {
        "valid": not missing and bool(references_content),
        "required_headings": len(headings),
        "headings_present": sum(present.values()),
        "missing_headings": missing,
        "references_section_has_content": bool(references_content),
        "note": (
            "Structural validation only; it does not prove "
            "that references or claims are accurate."
        ),
    }
