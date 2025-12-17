# 🔍 SiteCheck – Website Security Scanner (Django App)

SiteCheck is a simple Django-based application designed to perform **basic website vulnerability and security checks** by analyzing a given URL. It rates the site's security and provides useful recommendations based on best practices.

---

## 🚀 Features

### ✅ SSL/TLS Checks
- HTTPS enabled?
- SSL certificate validity and expiration
- Deprecated protocols detection (e.g., TLS 1.0)

### ✅ Security Headers Check
- Content-Security-Policy
- X-Frame-Options
- Strict-Transport-Security
- Referrer-Policy
- X-Content-Type-Options
- Permissions-Policy

### ✅ HTTPS Redirection
- HTTP → HTTPS forced redirection
- WWW and non-WWW consistency

### ✅ Open Ports Scan
- Scans for common open ports (e.g., 80, 443, 21, 22, etc.)

### ✅ Technology Fingerprinting
- Detects server type, CMS/framework, and frontend libraries

### ✅ Sensitive File Exposure
- Looks for publicly accessible files:
  - `/robots.txt`, `.env`, `.git/`, `backup.zip`, etc.

### ✅ XSS / SQLi Potential
- Checks form inputs
- Basic passive analysis for risky patterns

### ✅ Cookie Attributes
- Checks for Secure, HttpOnly, and SameSite

### ✅ CORS Policy
- Warns if `Access-Control-Allow-Origin: *`

### ✅ Recommendations Engine
- Rates the site's security
- Gives clear, actionable tips

---

## 🔧 Setup Instructions

### Step 1: Clone the Repo
```bash
git clone https://github.com/yourusername/sitecheck.git
cd sitecheck
```

---

## 🔍 Security Checks Implemented

The scanner currently supports the following categories of checks:

### ✅ SSL/TLS & HTTPS

* **SSL Certificate Validity**
* **Supported SSL Protocols**
* **HSTS (Strict-Transport-Security) Header**
* **HTTP to HTTPS Redirection**
* **WWW and non-WWW Redirect Consistency**

### 🔐 HTTP Security Headers

* **Content-Security-Policy (CSP)**
* **X-Frame-Options**
* **X-Content-Type-Options**
* **Strict-Transport-Security**
* **Referrer-Policy**
* **Permissions-Policy**

### 🍪 Cookie Security

* **Cookies with `Secure` attribute**
* **Cookies with `HttpOnly` attribute**
* **Cookies with `SameSite` attribute**

### 🧾 Input Validation & Forms

* **CSRF Token Presence**
* **Suspicious Form Input Parameters (Injection Risk)**

### 🖥️ Server Information Exposure

* **Server Header Technology Fingerprinting**
* **Sensitive/Exposed Files (e.g., `.git/`, `.env`, `backup.zip`)**

### 🌐 CORS Policy

* **Access-Control-Allow-Origin Header Check**

### 🔎 Port Scan

* **Common Open Ports Detection (e.g., 21, 22, 23, 80, 443, 3306, etc.)**

---

## 🚧 Upcoming Features

* **Email Security (DNS-based)**

  * DMARC Record Check
  * SPF Record Check
  * DKIM Record Check

* **Software/Library Security**

  * Detection of Outdated or Vulnerable Libraries (Front-end & Back-end)

---