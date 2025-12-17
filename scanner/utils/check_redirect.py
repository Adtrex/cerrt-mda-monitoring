# utils/redirect_checks.py

import httpx
from urllib.parse import urlparse

def normalize_domain(url: str) -> str:
    """Extract naked domain (e.g., example.com) from input"""
    parsed = urlparse(url if url.startswith("http") else f"http://{url}")
    domain = parsed.netloc or parsed.path
    return domain.replace("www.", "")


def https_redirect_check(url: str) -> dict:
    domain = normalize_domain(url)
    test_url = f"http://{domain}"

    try:
        response = httpx.get(test_url, follow_redirects=True, timeout=5)
        final_url = str(response.url)

        if final_url.startswith("https://"):
            return {
                "status": "pass",
                "overview": "Check if the site redirects HTTP to HTTPS",
                "details": f"Redirected to HTTPS: {final_url}",
                "recommendation": "No action needed."
            }
        else:
            return {
                "status": "fail",
                "overview": "Check if the site redirects HTTP to HTTPS",
                "details": f"Did not redirect to HTTPS. Final URL: {final_url}",
                "recommendation": "Configure HTTP to redirect to HTTPS in your server settings."
            }

    except Exception as e:
        return {
            "status": "fail",
            "overview": "Check if the site redirects HTTP to HTTPS",
            "details": f"Error checking HTTPS redirect: {e}",
            "recommendation": "Ensure your domain is reachable and handles HTTP correctly."
        }

def www_redirect_check(url: str) -> dict:
    domain = normalize_domain(url)
    www_url = f"http://www.{domain}"
    non_www_url = f"http://{domain}"

    try:
        www_response = httpx.get(www_url, follow_redirects=True, timeout=5)
        non_www_response = httpx.get(non_www_url, follow_redirects=True, timeout=5)

        if str(www_response.url) == str(non_www_response.url):
            return {
                "status": "pass",
                "overview": "Check if the site redirects HTTP to HTTPS",
                "details": "Consistent redirect between www and non-www.",
                "recommendation": "No action needed."
            }
        else:
            return {
                "status": "fail",
                "overview": "Check if the site redirects HTTP to HTTPS",
                "details": (
                    f"Inconsistent redirect:\n"
                    f"  www → {www_response.url}\n"
                    f"  non-www → {non_www_response.url}"
                ),
                "recommendation": "Choose one (www or non-www) and configure consistent redirection."
            }

    except Exception as e:
        return {
            "status": "fail",
            "overview": "Check if the site redirects HTTP to HTTPS",
            "details": f"Error checking WWW redirect: {e}",
            "recommendation": "Ensure both www and non-www versions are reachable and redirect consistently."
        }
