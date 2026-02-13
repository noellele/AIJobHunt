"""
Canonical Job Posting schema for MongoDB.

All API ingestion scripts should map to this shape before writing.
Schema:
  external_id: str (unique; composite "{source}_{raw_id}" so ids are unique across platforms)
  title: str
  company: str
  description: str
  location: str
  remote_type: str ("remote" | "hybrid" | "onsite" | "")
  skills_required: list[str]
  posted_date: datetime (UTC) or None
  source_url: str
  source_platform: str (same as source — e.g. "Adzuna", "SerpAPI")
  salary_range: { min: number | None, max: number | None, currency: str }
  source: str (source identifier; source_platform = source)
  ingested_at: datetime (set by ingestion)
"""

import csv
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


def _parse_date(value: Any) -> Optional[datetime]:
    """Parse various date formats to UTC datetime. Returns None if unparseable."""
    if value is None or value == "" or value == "N/A":
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value).strip()
    if not s:
        return None
    # ISO format
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ):
        try:
            dt = datetime.strptime(s.replace("Z", "+00:00"), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError):
            continue
    return None


def _tags_to_skills(tags: Any) -> List[str]:
    """Convert Tags (string or list) to skills_required list."""
    if tags is None or tags == "":
        return []
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if t and str(t).strip()]
    s = str(tags).strip()
    if not s:
        return []
    return [p.strip() for p in re.split(r"[;,]", s) if p.strip()]


def _infer_remote_type(location: str) -> str:
    """Infer remote_type from location string."""
    if not location:
        return ""
    loc = (location or "").lower()
    if "remote" in loc or "anywhere" in loc or loc == "n/a":
        return "remote"
    if "hybrid" in loc:
        return "hybrid"
    return "onsite"


def _to_number(value: Any) -> Optional[float]:
    """Convert value to number for salary. Returns None if not a number."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_canonical_document(normalized: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Map normalizer output (Company, Position, Location, Tags, etc.) to the canonical DB schema.

    Accepts the current shape from all API normalizers (e.g. Company, Position, URL, Salary_Min, Date, ID).
    Returns a document ready for MongoDB with: external_id, title, company, description, location,
    remote_type, skills_required, posted_date, source_url, source_platform, salary_range.
    """
    title = (
        normalized.get("Position")
        or normalized.get("title")
        or normalized.get("PositionTitle")
        or ""
    )
    company = (
        normalized.get("Company")
        or normalized.get("company")
        or normalized.get("company_name")
        or normalized.get("OrganizationName")
        or ""
    )
    raw_id = (
        normalized.get("ID")
        or normalized.get("id")
        or normalized.get("PositionID")
        or ""
    )
    # composite external_id so the same raw id from different sources stays unique
    external_id = f"{source}_{raw_id}" if raw_id else f"{source}_{uuid.uuid4().hex}"
    description = (
        normalized.get("Description")
        or normalized.get("description")
        or ""
    )
    location = (
        normalized.get("Location")
        or normalized.get("location")
        or "Remote"
    )
    if location in ("", "N/A"):
        location = "Remote"
    remote_type = _infer_remote_type(location)
    skills_required = _tags_to_skills(
        normalized.get("Tags")
        or normalized.get("tags")
        or normalized.get("JobCategory")
        or []
    )
    posted_date = _parse_date(
        normalized.get("Date")
        or normalized.get("posted_date")
        or normalized.get("publication_date")
        or normalized.get("created")
    )
    source_url = (
        normalized.get("URL")
        or normalized.get("url")
        or normalized.get("source_url")
        or ""
    )
    min_sal = _to_number(normalized.get("Salary_Min") or normalized.get("salary_min"))
    max_sal = _to_number(normalized.get("Salary_Max") or normalized.get("salary_max"))
    # Schema: salary_range { min, max, currency } — currency always USD
    salary_range = {
        "min": min_sal,
        "max": max_sal,
        "currency": "USD",
    }

    # Exactly the schema written to MongoDB (plus source + ingested_at added by ingestion)
    return {
        "external_id": str(external_id),
        "title": str(title),
        "company": str(company),
        "description": str(description),
        "location": str(location),
        "remote_type": remote_type,
        "skills_required": skills_required,
        "posted_date": posted_date,  # datetime or None; MongoDB stores as ISODate
        "source_url": str(source_url),
        "source_platform": source,
        "salary_range": salary_range,
    }


# Canonical CSV column order (same schema as DB, flattened for CSV)
CANONICAL_CSV_FIELDS = [
    "external_id",
    "title",
    "company",
    "description",
    "location",
    "remote_type",
    "skills_required",
    "posted_date",
    "source_url",
    "source_platform",
    "salary_min",
    "salary_max",
    "salary_currency",
]


def _canonical_doc_to_csv_row(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten a canonical document for one CSV row."""
    sr = doc.get("salary_range") or {}
    posted = doc.get("posted_date")
    posted_str = posted.isoformat() if isinstance(posted, datetime) else (str(posted) if posted else "")
    skills = doc.get("skills_required") or []
    skills_str = "; ".join(str(s) for s in skills) if isinstance(skills, list) else str(skills)
    return {
        "external_id": doc.get("external_id", ""),
        "title": doc.get("title", ""),
        "company": doc.get("company", ""),
        "description": doc.get("description", ""),
        "location": doc.get("location", ""),
        "remote_type": doc.get("remote_type", ""),
        "skills_required": skills_str,
        "posted_date": posted_str,
        "source_url": doc.get("source_url", ""),
        "source_platform": doc.get("source_platform", ""),
        "salary_min": sr.get("min") if sr.get("min") is not None else "",
        "salary_max": sr.get("max") if sr.get("max") is not None else "",
        "salary_currency": sr.get("currency", "USD"),
    }


def export_canonical_to_csv(
    jobs: List[Dict[str, Any]],
    source: str,
    normalizer: Callable[[Dict[str, Any]], Dict[str, Any]],
    csv_dir: str,
    filename: Optional[str] = None,
    file_prefix: Optional[str] = None,
) -> str:
    """
    Export jobs to CSV using the canonical schema (same as MongoDB).

    Each job is normalized with the given normalizer, then mapped to the canonical
    document shape; rows are flattened for CSV (skills_required as semicolon-separated,
    posted_date as ISO string, salary_range as salary_min, salary_max, salary_currency).

    Args:
        jobs: Raw job records from the API.
        source: Source label (e.g. "Adzuna", "SerpAPI"); becomes source_platform.
        normalizer: Function that takes one raw job dict and returns a normalized dict.
        csv_dir: Directory path to write the CSV file into.
        filename: Optional full filename (e.g. "adzuna_20260210.csv"). If None, generated.
        file_prefix: Optional prefix for auto filename (e.g. "adzuna_top_jobs"); default source.

    Returns:
        Absolute path to the created CSV file, or "" if no jobs.
    """
    if not jobs:
        return ""
    os.makedirs(csv_dir, exist_ok=True)
    prefix = (file_prefix or source).replace(" ", "_").lower()
    if not filename:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H_%M_%S")
        filename = f"{prefix}_{timestamp}.csv"
    filepath = os.path.join(csv_dir, filename)
    canonical_docs = [to_canonical_document(normalizer(job), source) for job in jobs]
    rows = [_canonical_doc_to_csv_row(doc) for doc in canonical_docs]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return os.path.abspath(filepath)
