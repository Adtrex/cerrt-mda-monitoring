# scans/utils.py
from urllib.parse import urlparse

def normalize_url(raw_url: str) -> str:
    """
    Normalize the input to ensure it has a scheme (https://) and a hostname.
    - If no scheme, default to https://
    - Strips path/query if present, only keeps scheme://hostname
    """
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url

    parsed = urlparse(raw_url)
    if not parsed.hostname:
        raise ValueError(f"Invalid URL: {raw_url}")

    # Always return scheme://hostname (ignore path/query for scanning)
    return f"{parsed.scheme}://{parsed.hostname}"
