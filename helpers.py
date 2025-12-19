"""
Helper utility functions for CUSB Research Analyzer
"""
import re
from datetime import datetime
from typing import Optional


def format_number(num: int) -> str:
    """Format numbers with comma separators for readability."""
    if num is None:
        return "0"
    return "{:,}".format(num)


def format_date(date_str: Optional[str] = None) -> str:
    """Format date string to a readable format."""
    if date_str is None:
        return datetime.now().strftime("%B %d, %Y")
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    return sanitized[:100]


def calculate_h_index(citations: list) -> int:
    """Calculate h-index from a list of citation counts."""
    if not citations:
        return 0
    sorted_citations = sorted(citations, reverse=True)
    h_index = 0
    for i, cite_count in enumerate(sorted_citations, 1):
        if cite_count >= i:
            h_index = i
        else:
            break
    return h_index


def calculate_i10_index(citations: list) -> int:
    """Calculate i10-index (papers with at least 10 citations)."""
    if not citations:
        return 0
    return sum(1 for c in citations if c >= 10)


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def parse_year(year_str) -> Optional[int]:
    """Parse year from various formats."""
    if year_str is None:
        return None
    if isinstance(year_str, int):
        return year_str
    try:
        return int(str(year_str)[:4])
    except (ValueError, TypeError):
        return None


def get_year_range(publications: list) -> tuple:
    """Get the year range from a list of publications."""
    years = [p.get('year') for p in publications if p.get('year')]
    years = [parse_year(y) for y in years]
    years = [y for y in years if y is not None]
    if not years:
        return (datetime.now().year - 10, datetime.now().year)
    return (min(years), max(years))
