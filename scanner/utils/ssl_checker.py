import ssl
import socket
import certifi
import requests
from urllib.parse import urlparse
from datetime import datetime


# -----------------------------
# HELPERS
# -----------------------------
def normalize_url(url):
    """Ensure URL has https:// and return (clean_url, parsed_url)."""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)
    return url, parsed


# -----------------------------
# SSL CERTIFICATE VALIDITY CHECK
# -----------------------------
def check_ssl_validity(url):
    try:
        url, parsed_url = normalize_url(url)
        hostname = parsed_url.hostname

        if not hostname:
            return {
                "status": "fail",
                "overview": "Check SSL certificate validity to ensure secure connections.",
                "details": "Invalid URL — hostname could not be extracted.",
                "recommendation": "Enter a valid domain (e.g. https://example.com)."
            }

        context = ssl.create_default_context(cafile=certifi.where())

        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (expires - datetime.utcnow()).days

                return {
                    "status": "pass" if days_left > 0 else "fail",
                    "overview": "Check SSL certificate validity to ensure secure connections.",
                    "details": f"Certificate expires in {days_left} days on {expires.strftime('%Y-%m-%d')}.",
                    "recommendation": (
                        "Renew soon." if days_left <= 30 else "Certificate is valid."
                    )
                }

    except socket.gaierror as e:
        return {
            "status": "fail",
            "overview": "Check SSL certificate validity.",
            "details": f"DNS lookup failed: {e}",
            "recommendation": "Verify domain spelling or DNS records."
        }

    except ssl.SSLError as e:
        return {
            "status": "fail",
            "overview": "Check SSL certificate validity.",
            "details": f"SSL error: {e}",
            "recommendation": "Install a valid SSL certificate from a trusted CA."
        }

    except Exception as e:
        return {
            "status": "fail",
            "overview": "Check SSL certificate validity.",
            "details": f"Unexpected error: {e}",
            "recommendation": "Investigate SSL configuration."
        }


# -----------------------------
# SSL/TLS PROTOCOL SUPPORT CHECK
# -----------------------------
def check_ssl_protocols(url):
    url, parsed = normalize_url(url)
    hostname = parsed.hostname

    if not hostname:
        return {
            "status": "fail",
            "overview": "Check supported SSL/TLS protocols.",
            "details": "Invalid URL.",
            "supported_protocols": [],
            "recommendation": "Use a valid URL such as https://example.com."
        }

    supported = []
    protocol_map = {
        "TLSv1": ssl.PROTOCOL_TLSv1,
        "TLSv1_1": ssl.PROTOCOL_TLSv1_1,
        "TLSv1_2": ssl.PROTOCOL_TLSv1_2,
        "TLSv1_3": ssl.PROTOCOL_TLS_CLIENT  # Negotiates best available
    }

    for name, version in protocol_map.items():
        try:
            context = ssl.SSLContext(version)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(certifi.where())

            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname):
                    supported.append(name)

        except Exception:
            pass  # Protocol unsupported

    recommendation = generate_ssl_protocol_recommendation(supported)

    if supported:
        return {
            "status": "pass",
            "overview": "Check supported SSL/TLS protocols.",
            "details": f"Supported: {', '.join(supported)}",
            "supported_protocols": supported,
            "recommendation": recommendation,
        }

    return {
        "status": "fail",
        "overview": "Check supported SSL/TLS protocols.",
        "details": f"No protocols supported or connection refused.",
        "supported_protocols": [],
        "recommendation": "Ensure server supports TLS 1.2 or TLS 1.3."
    }


def generate_ssl_protocol_recommendation(supported):
    weak = {"TLSv1", "TLSv1_1"}
    modern = {"TLSv1_2", "TLSv1_3"}

    has_weak = any(p in supported for p in weak)
    has_modern = any(p in supported for p in modern)

    if has_modern and not has_weak:
        return "Server uses strong TLS protocols. No action needed."
    if has_modern and has_weak:
        return "Disable outdated TLS 1.0/1.1 protocols."
    if has_weak and not has_modern:
        return "Server is insecure. Upgrade to TLS 1.2 or 1.3."
    return "Unable to determine protocol strength."


# -----------------------------
# HSTS CHECK
# -----------------------------
def check_hsts_enabled(url):
    url, parsed = normalize_url(url)

    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        hsts = response.headers.get("Strict-Transport-Security")

        if hsts:
            return {
                "status": "pass",
                "overview": "Check if HSTS is enabled.",
                "details": f"HSTS enabled: {hsts}",
                "recommendation": "HSTS is properly configured."
            }

        return {
            "status": "fail",
            "overview": "Check if HSTS is enabled.",
            "details": "HSTS header not found.",
            "recommendation": "Enable HSTS for improved HTTPS security."
        }

    except requests.exceptions.Timeout:
        return {
            "status": "fail",
            "overview": "Check if HSTS is enabled.",
            "details": "Connection timed out.",
            "recommendation": "Check server responsiveness."
        }

    except Exception as e:
        return {
            "status": "fail",
            "overview": "Check if HSTS is enabled.",
            "details": f"Error: {e}",
            "recommendation": "Verify server accessibility."
        }
