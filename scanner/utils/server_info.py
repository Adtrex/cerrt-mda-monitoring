import httpx
from urllib.parse import urlparse

def normalize_domain(url: str) -> str:
    """Ensure domain is normalized with scheme (https://) and no trailing slash."""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path
    return f"{scheme}://{netloc}"

def check_server_header_info(url: str) -> dict:
    """
    Detects the server software and technologies exposed in response headers.

    Args:
        url (str): The URL of the website.

    Returns:
        dict: Contains status, details, and recommendation about server fingerprinting.
    """
    url = normalize_domain(url)

    try:
        response = httpx.get(url, timeout=5)
        headers = response.headers

        fingerprint_info = []

        server_header = headers.get("Server")
        powered_by = headers.get("X-Powered-By")
        via = headers.get("Via")
        aspnet_version = headers.get("X-AspNet-Version")

        # Aggregate identifiable headers
        if server_header:
            fingerprint_info.append(f"Server: {server_header}")
        if powered_by:
            fingerprint_info.append(f"X-Powered-By: {powered_by}")
        if via:
            fingerprint_info.append(f"Via: {via}")
        if aspnet_version:
            fingerprint_info.append(f"X-AspNet-Version: {aspnet_version}")

        # Risk assessment: If any version info is found
        risky = any(
            any(char.isdigit() for char in h) for h in [server_header, powered_by, aspnet_version] if h
        )

        if fingerprint_info:
            return {
                "status": "fail" if risky else "warning",
                "overview": "Check for identifiable server information in response headers. Exposing server details can lead to fingerprinting attacks.",
                "details": f"Identifiable server info found:\n" + "\n".join(fingerprint_info),
                "recommendation": (
                    "Consider removing or obfuscating server headers using reverse proxy or server config.\n"
                    "Avoid exposing software version numbers."
                ),
            }
        else:
            return {
                "status": "pass",
                "overview": "Check for identifiable server information in response headers. Exposing server details can lead to fingerprinting attacks.",
                "details": "No identifiable server headers found. Server fingerprinting is minimized.",
                "recommendation": "Good practice. Continue to monitor for leakage via other vectors (e.g., error pages)."
            }

    except httpx.RequestError as e:
        return {
            "status": "fail",
            "overview": "Check for identifiable server information in response headers. Exposing server details can lead to fingerprinting attacks.",
            "details": f"Request error during server info check: {e}",
            "recommendation": "Ensure the server is online and reachable from the scanner."
        }

import httpx
from urllib.parse import urljoin, urlparse

def check_exposed_files_check(base_url: str) -> dict:
    """
    Check for sensitive or misconfigured files that are publicly accessible.

    Args:
        base_url (str): The website URL (e.g. 'example.com').

    Returns:
        dict: A dictionary with scan results.
    """
    base_url = normalize_domain(base_url)

    common_sensitive_paths = [
        '.env',             # Environment config
        '.git/config',      # Git repo config
        '.htaccess',        # Apache directives
        'config.php',       # PHP config
        'wp-config.php',    # WordPress config
        'composer.json',    # PHP dependency manager
        'package.json',     # Node.js
        'server-status',    # Apache status
        'admin/.env',       # Deeply nested env
        'backup.zip',       # Backup files
        'db.sql',           # DB dump
        '.DS_Store',        # macOS metadata
    ]

    exposed_files = []

    for path in common_sensitive_paths:
        target_url = urljoin(base_url + '/', path)
        try:
            response = httpx.get(target_url, timeout=5, follow_redirects=True)
            if response.status_code == 200 and len(response.content) > 0:
                snippet = response.text[:100].strip().replace('\n', ' ')
                exposed_files.append((path, snippet))
        except httpx.RequestError:
            continue  # Ignore timeouts or connection errors

    if exposed_files:
        details = "\n".join([f"{file}: {preview}" for file, preview in exposed_files])
        return {
            "status": "fail",
            "overview": "Check for exposed sensitive files that should not be publicly accessible. Exposed files can lead to information leakage and security risks.",
            "details": f"Exposed sensitive files detected:\n{details}",
            "recommendation": (
                "Immediately restrict access to these files via server config or move them outside public directories.\n"
                "Use .gitignore and automated CI/CD rules to prevent publishing internal files."
            )
        }
    else:
        return {
            "status": "pass",
            "overview": "Check for exposed sensitive files that should not be publicly accessible. Exposed files can lead to information leakage and security risks.",
            "details": "No sensitive files appear to be publicly accessible.",
            "recommendation": "Keep scanning regularly and monitor server configuration changes."
        }
