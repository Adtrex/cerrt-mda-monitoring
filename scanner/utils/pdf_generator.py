import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, ListStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_security_report_pdf(url, scan_results):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomHeading1', fontSize=14, spaceAfter=8, leading=16, alignment=1, fontName='Helvetica-Bold'))  # Centered
    styles.add(ParagraphStyle(name='CustomHeading2', fontSize=12, spaceAfter=8, leading=16, spaceBefore=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='CustomNormal', fontSize=12, spaceAfter=8, leading=14, alignment=4))  # 4 = JUSTIFY
    styles.add(ParagraphStyle(name='CustomBullet', fontSize=12, leftIndent=20, spaceAfter=4, leading=14, alignment=4))  # 4 = JUSTIFY
    styles.add(ParagraphStyle(name='CustomDate', fontSize=12, spaceAfter=12, alignment=1))  # Centered
    list_style = ListStyle(
        'list_style',
        bulletType='bullet', # Can also be 'circle', 'square', '1', 'a', etc.
        bulletFontName='Helvetica',
        bulletFontSize=10,
        bulletIndent=0.25 * inch, # Indent the bullet itself
        leftIndent=0.5 * inch,    # Indent the entire list from the left margin
        rightIndent=0,
        bulletColor='black',
        bulletOffsetY=-2,
    )
    
    elements = []

    # Extract domain name
    domain_name = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    
    # Date with ordinal suffix
    day = datetime.datetime.now().day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    elif day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    current_date = datetime.datetime.now().strftime(f'%d{suffix} %B %Y')
    
    # Title
    elements.append(Paragraph(f"Report on Website Security Vulnerabilities for {domain_name.upper()}", styles['CustomHeading1']))
    elements.append(Paragraph(current_date, styles['CustomDate']))
    elements.append(Spacer(1, 0.1 * inch))

    # Intro
    intro_text = (
        f"During our routine monitoring of the {domain_name.upper()} domain ({url}), "
        "we have identified some critical security vulnerabilities that require immediate attention. "
        "These vulnerabilities pose significant risks to the security and privacy of the website's users "
        "and could potentially lead to unauthorized access or the compromise of sensitive information."
    )
    elements.append(Paragraph(intro_text, styles['CustomNormal']))
    
    # Preliminary Findings
    elements.append(Paragraph("Preliminary Findings", styles['CustomHeading2']))
    # elements.append(Spacer(1, 0.1 * inch))

    # --- 1. Outdated Software Packages ---
    if 'frontend_libraries' in scan_results:
        elements.append(Paragraph("1. Outdated Software Packages", styles['CustomHeading2']))
        
        outdated_libs = []
        scan_result = scan_results.get('frontend_libraries', {}).get('result', {}) or {}
        for lib in scan_result.get('results', []):
            if lib.get('status') == 'outdated':
                outdated_libs.append(f"{lib['name']} (Version {lib['detected_version']})")

        if outdated_libs:
            lib_text = (
                "We observed the presence of " + 
                ("multiple obsolete software packages" if len(outdated_libs) > 1 else "an obsolete software package") +
                " on the website, these " +
                ("include" if len(outdated_libs) > 1 else "includes") +
                f" {', '.join(outdated_libs)}. " +
                ("These outdated versions are" if len(outdated_libs) > 1 else "This outdated version is") +
                " known to contain vulnerabilities that can be exploited by attackers "
                "to gain unauthorized access to the website or compromise user data."
            )
        else:
            lib_text = (
                "We observed the presence of multiple software packages on the website. "
                "All detected libraries appear to be up to date with no known critical vulnerabilities."
            )
        elements.append(Paragraph(lib_text, styles['CustomNormal']))

    # --- 2. Missing Security Headers ---
    if 'security_headers' in scan_results:
        elements.append(Paragraph("2. Missing Security Headers", styles['CustomHeading2']))

        missing_headers = []
        for header in scan_results['security_headers']['result'].get('results', []):
            if header.get('status') in ('fail', 'missing'):
                header_name = header['check']
                if 'x-frame-options' in header_name.lower():
                    missing_headers.append('X-Frame-Options')
                elif 'referrer-policy' in header_name.lower():
                    missing_headers.append('Referrer-Policy')
                elif 'permissions-policy' in header_name.lower():
                    missing_headers.append('Permissions-Policy')
                elif 'content-security-policy' in header_name.lower():
                    missing_headers.append('Content Security Policy')
                elif 'strict-transport-security' in header_name.lower():
                    missing_headers.append('Strict Transport Security')
                elif 'x-content-type-options' in header_name.lower():
                    missing_headers.append('X-Content-Type-Options')
                else:
                    missing_headers.append(header_name)

        if missing_headers:
            missing_headers = list(dict.fromkeys(missing_headers))
            header_text = (
                f"Our routine monitoring has revealed that the {domain_name.upper()} domain is not implementing "
                f"crucial security headers, including {', '.join(missing_headers)}. "
                "These headers play a vital role in safeguarding the website against various types of attacks, "
                "such as cross-site scripting (XSS), clickjacking, and referrer leaks."
            )
            elements.append(Paragraph(header_text, styles['CustomNormal']))
        else:
            elements.append(Paragraph("All essential security headers appear to be properly implemented.", styles['CustomNormal']))
        elements.append(Spacer(1, 0.15 * inch))

    # --- 3. Email Authentication ---
    if 'email_security' in scan_results:
        elements.append(Paragraph("3. Email Authentication Methods", styles['CustomHeading2']))
        email_data = scan_results['email_security']
        
        # Normalize structure
        if isinstance(email_data, dict) and 'result' in email_data:
            email_results = email_data['result']
        else:
            email_results = email_data

        checks_summary = []
        missing_records = []

        if 'results' in email_results and email_results['results']:
            for result in email_results['results']:
                check_name = result.get('check', 'Unknown')
                status = result.get('status', 'fail')
                
                if status == 'pass':
                    checks_summary.append(f"• {check_name} record found")
                else:
                    checks_summary.append(f"• No {check_name} record found")
                    missing_records.append(check_name)

        # Add the bulleted checks (SPF, DKIM, DMARC etc.)
        for summary in checks_summary:
            elements.append(Paragraph(summary, styles['CustomBullet']))

        # Explanatory text for missing records
        if missing_records:
            explanations = []
            if 'DMARC' in missing_records:
                explanations.append(
                    "The absence of a Domain-based Message Authentication, Reporting and Conformance (DMARC) record "
                    "indicates a lack of specific instructions from the domain owner regarding email handling, "
                    "potentially leaving the domain vulnerable to malicious activities."
                )
            if 'DKIM' in missing_records:
                explanations.append(
                    "The absence of DomainKeys Identified Mail (DKIM) records suggests that the domain owner has not "
                    "implemented this additional layer of authentication. Without DKIM signatures, there is an increased "
                    "risk of email tampering and spoofing, potentially compromising the trustworthiness of communications."
                )
            if 'SPF' in missing_records:
                explanations.append(
                    "The absence of a Sender Policy Framework (SPF) record makes it difficult to prevent spammers "
                    "from forging messages that appear to come from the domain."
                )

            # Join all explanations into one paragraph
            elements.append(Paragraph(" ".join(explanations), styles['CustomNormal']))
    

        # --- Recommendations ---
    elements.append(Paragraph("Recommendations", styles['CustomHeading2']))
    recommendations = []

    # Outdated libraries
    if outdated_libs:
        recommendations.append(
            "It is strongly recommended that the identified software packages be updated to their latest versions. "
            "This action will help mitigate the risk associated with known vulnerabilities and ensure the overall "
            "security of your website."
        )
        
    # Missing security headers
    if missing_headers:
        recommendations.append(
            f"Implement the missing security headers ({', '.join(missing_headers)}) on the {domain_name.upper()} domain. "
            "These headers are vital in protecting the site against XSS, clickjacking, and data leakage attacks."
        )

    # Missing email records
    if missing_records:
        if "SPF" in missing_records:
            recommendations.append("Add an SPF record to prevent spammers from forging emails from your domain.")
        if "DKIM" in missing_records:
            recommendations.append("Add a DKIM record to ensure email integrity and reduce spoofing risks.")
        if "DMARC" in missing_records:
            recommendations.append("Add a DMARC record to provide email handling instructions and protect against phishing.")

    # Always add general recommendation
    recommendations.append(
        "Conduct a Vulnerability Assessment and Penetration Testing (VAPT) to identify and address additional security weaknesses."
    )

    # Render recommendations
    list_items = []
    for rec in recommendations:
        list_items.append(ListItem(Paragraph(rec, style=ParagraphStyle(
            name='CustomListItem',
            fontSize=12,
            leading=16,
            leftIndent=-10, # Reduce space between bullet and text
            rightIndent=20,
            alignment=4, # 4 = JUSTIFY
            spaceAfter=8
        ))))
        
    elements.append(ListFlowable(
        list_items,
        style=list_style
    ))


    # Conclusion
    elements.append(Paragraph("Conclusion", styles['CustomHeading2']))
    conclusion = (
        "Addressing the identified vulnerabilities is essential to mitigate potential security risks "
        "and uphold trust and integrity of your website. We strongly recommend you to take immediate action "
        "to implement the recommended measures."
    )
    elements.append(Paragraph(conclusion, styles['CustomNormal']))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
