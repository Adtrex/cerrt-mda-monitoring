# scans/__init__.py
from .registry import register
from scanner.utils.headers import check_security_headers
from scanner.utils.email_security import check_email_security
from scanner.utils.frontend_libraries import scan_frontend_libraries
from scanner.utils.ssl_checker import (
    check_ssl_validity,
    check_ssl_protocols,
    check_hsts_enabled
)

# Wrapper to unify the SSL data in one response
def ssl_info_action(url):
    try:
        validity = check_ssl_validity(url)
        protocols = check_ssl_protocols(url)
        hsts = check_hsts_enabled(url)

        return {
            "status": "ok",
            "result": {
                "validity": validity,
                "protocols": protocols,
                "hsts": hsts,
                "summary": {
                    "score": 90  # you can compute a real score later
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Register existing actions
register("security_headers", check_security_headers, timeout=20)
register("email_security", check_email_security, timeout=30)
register("frontend_libraries", scan_frontend_libraries, timeout=60)

# Register SSL
register("ssl_info", ssl_info_action, timeout=40)
