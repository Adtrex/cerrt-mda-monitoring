import aiohttp
from typing import Dict, List, Any

SECURITY_HEADERS = {
    "content-security-policy": {
        "overview": "Helps prevent XSS attacks by specifying valid content sources.",
        "risk_if_missing": "High",
        "weight": 3
    },
    "x-frame-options": {
        "overview": "Mitigates clickjacking attacks by controlling if the site can be embedded in frames.",
        "risk_if_missing": "Medium",
        "weight": 2
    },
    "x-content-type-options": {
        "overview": "Prevents MIME type sniffing which can lead to drive-by download attacks.",
        "risk_if_missing": "Medium",
        "weight": 2
    },
    "referrer-policy": {
        "overview": "Controls the amount of referrer information sent with requests.",
        "risk_if_missing": "Low",
        "weight": 1
    },
    "permissions-policy": {
        "overview": "Restricts or grants access to browser features like geolocation, camera, or microphone.",
        "risk_if_missing": "Low",
        "weight": 1
    },
    "strict-transport-security": {
        "overview": "Enforces HTTPS usage and prevents protocol downgrade attacks.",
        "risk_if_missing": "High",
        "weight": 3
    }
}

def _generate_general_recommendation(score: int) -> str:
    if score >= 90:
        return "Excellent! Your site has a strong security header configuration. 🚀"
    elif score >= 70:
        return "Good. Only minor improvements are needed for optimal protection."
    elif score >= 40:
        return "Warning. Some important security headers are missing. Addressing these will significantly improve your site's resilience against common web attacks. ⚠️"
    else:
        return "Critical. Immediate action is recommended to reduce the risk of XSS, clickjacking, and downgrade attacks. 🚨"

def _generate_failure_response(url: str, error_msg: str) -> Dict[str, Any]:
    """Generates a consistent failure response structure."""
    return {
        "action": "security_headers",
        "target": url,
        "summary": {
            "total_checks": len(SECURITY_HEADERS),
            "passed": 0,
            "failed": len(SECURITY_HEADERS),
            "score": 0,
            "risk_level": "High"
        },
        "results": [{
            "check": "Security Headers",
            "status": "fail",
            "overview": "Check for security headers to prevent common web vulnerabilities.",
            "details": error_msg,
            "recommendation": "Ensure the website is reachable and responding with a valid SSL certificate.",
            "risk": "High"
        }],
        "general_recommendation": "The scan failed; verify the URL and network settings and re-run."
    }

async def check_security_headers(url: str) -> Dict:
    results: List[Dict] = []
    
    # Timeout configuration: a total timeout is often sufficient and simpler
    timeout = aiohttp.ClientTimeout(total=20) 

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=False) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                
                # Weighted scoring
                max_score = sum(h['weight'] for h in SECURITY_HEADERS.values())
                current_score = 0
                
                for header, info in SECURITY_HEADERS.items():
                    if header in headers:
                        current_score += info["weight"]
                        results.append({
                            "check": header,
                            "status": "pass",
                            "overview": info["overview"],
                            "details": f"`{header}` is present.",
                            "recommendation": None,
                            "risk": "Low"
                        })
                    else:
                        results.append({
                            "check": header,
                            "status": "fail",
                            "overview": info["overview"],
                            "details": f"`{header}` is missing.",
                            "recommendation": f"Consider adding `{header}`. {info['overview']}",
                            "risk": info["risk_if_missing"]
                        })

    except aiohttp.ClientConnectorError as e:
        return _generate_failure_response(url, f"Connection failed: {e}")
    except aiohttp.ClientError as e:
        return _generate_failure_response(url, f"Client error: {e}")
    except Exception as e:
        return _generate_failure_response(url, f"An unexpected error occurred: {e}")

    # Final summary calculation
    score = int((current_score / max_score) * 100) if max_score > 0 else 0
    passed = sum(1 for r in results if r["status"] == "pass")
    
    overall_risk = "Low"
    if score < 40:
        overall_risk = "High"
    elif score < 70:
        overall_risk = "Medium"

    return {
        "action": "security_headers",
        "target": url,
        "summary": {
            "total_checks": len(SECURITY_HEADERS),
            "passed": passed,
            "failed": len(SECURITY_HEADERS) - passed,
            "score": score,
            "risk_level": overall_risk
        },
        "results": results,
        "general_recommendation": _generate_general_recommendation(score)
    }