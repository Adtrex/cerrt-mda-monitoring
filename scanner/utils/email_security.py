# scanner/email_security.py
import dns.resolver
import re
from typing import Dict, Any, List, Optional

# Register with the action registry
from scanner.registry import register

# DMARC Check
def check_dmarc(domain: str) -> Dict[str, Any]:
    """
    Check DMARC record for a domain
    """
    try:
        # Query _dmarc.domain for TXT records
        answers = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
        dmarc_record = None
        
        # Find the DMARC record
        for rdata in answers:
            record = rdata.to_text().strip('"')
            if record.startswith('v=DMARC1'):
                dmarc_record = record
                break
        
        if not dmarc_record:
            return {
                "status": "fail",
                "check": "DMARC",
                "details": "No valid DMARC record found",
                "recommendation": "Implement a DMARC policy to protect your domain from email spoofing"
            }
        
        # Parse DMARC record
        policy = re.search(r'p=(\w+)', dmarc_record)
        policy_value = policy.group(1) if policy else "none"
        
        # Evaluate policy strength
        if policy_value == "reject":
            status = "pass"
            details = "Strong DMARC policy (reject) implemented"
            recommendation = "Your DMARC configuration is strong"
        elif policy_value == "quarantine":
            status = "pass"
            details = "Medium DMARC policy (quarantine) implemented"
            recommendation = "Consider upgrading to a 'reject' policy for stronger protection"
        else:  # none or missing
            status = "fail"
            details = f"Weak DMARC policy ({policy_value}) implemented"
            recommendation = "Upgrade to 'quarantine' or 'reject' policy for better protection"
        
        return {
            "status": status,
            "check": "DMARC",
            "details": details,
            "recommendation": recommendation,
            "raw_record": dmarc_record
        }
    
    except dns.resolver.NXDOMAIN:
        return {
            "status": "fail",
            "check": "DMARC",
            "details": "No DMARC record found",
            "recommendation": "Implement a DMARC policy to protect your domain from email spoofing"
        }
    except Exception as e:
        return {
            "status": "error",
            "check": "DMARC",
            "details": f"Error checking DMARC: {str(e)}",
            "recommendation": "Check DNS configuration and try again"
        }

# SPF Check
def check_spf(domain: str) -> Dict[str, Any]:
    """
    Check SPF record for a domain
    """
    try:
        # Query domain for TXT records
        answers = dns.resolver.resolve(domain, 'TXT')
        spf_record = None
        
        # Find the SPF record
        for rdata in answers:
            record = rdata.to_text().strip('"')
            if record.startswith('v=spf1'):
                spf_record = record
                break
        
        if not spf_record:
            return {
                "status": "fail",
                "check": "SPF",
                "details": "No SPF record found",
                "recommendation": "Implement an SPF record to prevent email spoofing"
            }
        
        # Check for all mechanism (dangerous)
        if re.search(r'\s+[+-]?all\b', spf_record):
            all_mechanism = re.search(r'\s+([+-]?)all\b', spf_record).group(1)
            
            if all_mechanism == "-":
                status = "pass"
                details = "SPF record with -all (strict) found"
                recommendation = "Your SPF configuration is strong"
            elif all_mechanism == "~":
                status = "pass"
                details = "SPF record with ~all (soft fail) found"
                recommendation = "Consider upgrading to -all for stronger protection"
            elif all_mechanism == "+":
                status = "fail"
                details = "SPF record with +all (dangerous) found"
                recommendation = "Change +all to -all or ~all to prevent email spoofing"
            else:  # No qualifier (defaults to +)
                status = "fail"
                details = "SPF record with default +all (dangerous) found"
                recommendation = "Change +all to -all or ~all to prevent email spoofing"
        else:
            status = "fail"
            details = "SPF record without an 'all' mechanism found"
            recommendation = "Add -all or ~all to your SPF record to prevent email spoofing"
        
        return {
            "status": status,
            "check": "SPF",
            "details": details,
            "recommendation": recommendation,
            "raw_record": spf_record
        }
    
    except dns.resolver.NXDOMAIN:
        return {
            "status": "fail",
            "check": "SPF",
            "details": "Domain not found",
            "recommendation": "Check domain name and try again"
        }
    except Exception as e:
        return {
            "status": "error",
            "check": "SPF",
            "details": f"Error checking SPF: {str(e)}",
            "recommendation": "Check DNS configuration and try again"
        }

# DKIM Check
def check_dkim(domain: str) -> Dict[str, Any]:
    """
    Check DKIM record for a domain
    Note: This is a basic check as DKIM requires selector knowledge
    """
    # Common DKIM selectors to try
    common_selectors = ["default", "dkim", "mail", "email", "selector1", "selector2", "google"]
    found_selectors = []
    
    try:
        for selector in common_selectors:
            try:
                # Query selector._domainkey.domain for TXT records
                answers = dns.resolver.resolve(f"{selector}._domainkey.{domain}", 'TXT')
                for rdata in answers:
                    record = rdata.to_text().strip('"')
                    if "v=DKIM1" in record:
                        found_selectors.append({
                            "selector": selector,
                            "record": record
                        })
                        break
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                continue
            except Exception:
                continue
        
        if found_selectors:
            return {
                "status": "pass",
                "check": "DKIM",
                "details": f"Found {len(found_selectors)} DKIM selectors: {', '.join([s['selector'] for s in found_selectors])}",
                "recommendation": "Your DKIM configuration appears to be in place",
                "selectors": found_selectors
            }
        else:
            return {
                "status": "fail",
                "check": "DKIM",
                "details": "No DKIM records found with common selectors",
                "recommendation": "Implement DKIM to improve email deliverability and security"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "check": "DKIM",
            "details": f"Error checking DKIM: {str(e)}",
            "recommendation": "Check DNS configuration and try again"
        }

# Combined email security check
def check_email_security(domain: str) -> Dict[str, Any]:
    """
    Run all email security checks and return combined results
    """
    # Extract domain from URL if needed
    if domain.startswith("http"):
        from urllib.parse import urlparse
        parsed_url = urlparse(domain)
        domain = parsed_url.netloc
    
    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Run all checks
    dmarc_result = check_dmarc(domain)
    spf_result = check_spf(domain)
    dkim_result = check_dkim(domain)
    
    # Calculate score
    total_checks = 3
    passed_checks = sum(1 for check in [dmarc_result, spf_result, dkim_result] if check["status"] == "pass")
    score = int((passed_checks / total_checks) * 100)
    
    # Determine risk level
    if score >= 80:
        risk_level = "Low"
    elif score >= 50:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    # Generate general recommendation
    if score == 100:
        general_recommendation = "Your email security configuration is strong. Continue monitoring for best practices."
    elif score >= 80:
        general_recommendation = "Your email security is good but could be improved. Address the recommendations for failing checks."
    elif score >= 50:
        general_recommendation = "Your email security needs improvement. Implement the recommendations for failing checks."
    else:
        general_recommendation = "Your email security is weak. Urgently implement the recommendations for all failing checks."
    
    return {
        "summary": {
            "score": score,
            "passed": passed_checks,
            "failed": total_checks - passed_checks,
            "total_checks": total_checks,
            "risk_level": risk_level
        },
        "general_recommendation": general_recommendation,
        "results": [dmarc_result, spf_result, dkim_result]
    }

# Register the actions
register("dmarc", check_dmarc)
register("spf", check_spf)
register("dkim", check_dkim)
register("email_security", check_email_security)