from datetime import datetime
from pathlib import Path
import re
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"

def save_report(topic: str, report: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", topic.strip()).strip("_")[:60] or "research"
    path = OUTPUT_DIR / f"{slug}_{datetime.now():%Y%m%d_%H%M%S}.md"
    path.write_text(report.rstrip() + "\n", encoding="utf-8")
    return path
