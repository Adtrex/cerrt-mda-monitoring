import socket
from urllib.parse import urlparse

COMMON_PORTS = {
    21: 'FTP',
    22: 'SSH',
    23: 'Telnet',
    25: 'SMTP',
    53: 'DNS',
    80: 'HTTP',
    110: 'POP3',
    143: 'IMAP',
    443: 'HTTPS',
    465: 'SMTPS',
    587: 'SMTP Submission',
    993: 'IMAPS',
    995: 'POP3S',
    3306: 'MySQL',
    3389: 'RDP',
    5432: 'PostgreSQL',
    5900: 'VNC',
    6379: 'Redis',
    8080: 'HTTP-Alt',
    8443: 'HTTPS-Alt',
    9200: 'Elasticsearch',
    27017: 'MongoDB',
}

def check_open_ports(base_url: str) -> dict:
    """
    Scan a domain for common open ports that may indicate unnecessary exposure.

    Args:
        base_url (str): The domain or host name (without port).

    Returns:
        dict: Result indicating open ports and recommendations.
    """
    host = extract_hostname(base_url)
    open_ports = []

    for port, service in COMMON_PORTS.items():
        try:
            with socket.create_connection((host, port), timeout=1) as sock:
                open_ports.append((port, service))
        except (socket.timeout, ConnectionRefusedError, OSError):
            continue  # Port closed or filtered

    if not open_ports:
        return {
            "status": "pass",
            "overview": "Check for open ports to identify unnecessary exposure.",
            "details": "No common ports are open to the public.",
            "recommendation": "Maintain minimal exposure. Only expose services necessary for operation."
        }

    findings = "; ".join([f"{svc} (port {p})" for p, svc in open_ports])
    print(findings)	
    risky_ports = [p for p, _ in open_ports if p not in (80, 443)]
    status = "fail" if risky_ports else "warn"

    port_table = [
        {
            "port": p,
            "service": svc,
            "risk": (
                "Commonly targeted for attacks. Leaving this port open without reason may expose sensitive services."
                if p not in (80, 443) else
                "Standard web service port. Should only be open if serving HTTP/HTTPS traffic."
            )
        }
        for p, svc in open_ports
    ]

    return {
        "status": status,
        "result": f"Open ports detected: {findings}",
        "details": port_table,
        "recommendation": (
            "Restrict public access to non-essential ports using a firewall. "
            "Only expose ports needed for external functionality."
        )
    }

def extract_hostname(url: str) -> str:
    """Normalizes and extracts hostname from user input (example.com, with or without http/https)."""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return urlparse(url).hostname
