# SECURITY HEADER RESULT FORMAT
{
  "action": "security_headers",
  "target": "https://example.com",
  "summary": {
    "total_checks": 6,
    "passed": 4,
    "failed": 2,
    "score": 67,
    "risk_level": "Medium"
  },
  "results": [
    {
      "check": "Content-Security-Policy",
      "status": "pass",
      "overview": "Helps prevent XSS attacks by specifying valid content sources.",
      "details": "Content-Security-Policy is present.",
      "recommendation": null,
      "risk": "Low"
    },
    {
      "check": "X-Frame-Options",
      "status": "fail",
      "overview": "Mitigates clickjacking attacks by controlling if the site can be embedded in frames.",
      "details": "X-Frame-Options is missing.",
      "recommendation": "Consider adding X-Frame-Options. Mitigates clickjacking attacks by controlling if the site can be embedded in frames.",
      "risk": "Medium"
    }
  ],
  "general_recommendation": "Several important headers are missing. Implementing them will strengthen your defense against clickjacking, XSS, and protocol downgrade attacks."
}
# FRONTEND LIBRARIES RESULT FORMAT
{
  "action": "frontend_libraries",
  "target": "https://example.com",
  "summary": {
    "total_scripts": 12,
    "unique_libraries": 5,
    "with_detected_version": 3,
    "without_detected_version": 2,
    "up_to_date": 2,
    "outdated": 1,
    "unknown": 0,
    "score": 67,
    "risk_level": "Medium"
  },
  "general_recommendation": "Some libraries are outdated. Update libraries flagged as 'outdated' and review any unversioned libraries.",
  "results": [
    {
      "name": "jquery",
      "canonical": "jquery",
      "src_urls": [
        "https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js",
        "/static/js/jquery-3.5.1.min.js"
      ],
      "detection_methods": ["src_url_regex", "script_head_comment"],
      "detected_version": "3.5.1",
      "latest_version": "3.6.4",
      "status": "outdated",              # up-to-date | outdated | unknown | no-version
      "risk": "Medium",                  # Low/Medium/High - configurable per library
      "notes": "Detected multiple sources. CDN copy is outdated vs latest on cdnjs.",
      "recommendation": "Update jquery to latest 3.6.4; ensure no breaking changes."
    },
    {
      "name": "bootstrap",
      "canonical": "bootstrap",
      "src_urls": [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"
      ],
      "detection_methods": ["src_url_regex"],
      "detected_version": "5.2.3",
      "latest_version": "5.3.2",
      "status": "outdated",
      "risk": "Low",
      "notes": "",
      "recommendation": "Update to latest stable bootstrap; test UI after update."
    },
    {
      "name": "custom-lib",
      "canonical": null,
      "src_urls": [
        "/static/js/custom-lib.js"
      ],
      "detection_methods": ["inline_guess"],
      "detected_version": null,
      "latest_version": null,
      "status": "no-version",
      "risk": "Unknown",
      "notes": "No version found in src or header comments.",
      "recommendation": "Add versioned static assets or include version meta information."
    }
  ]
}
