# scanners/utils/frontend_libraries.py
import re
import asyncio
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import aiohttp

# If you want to add known libs, add canonical name -> search keys (lowercase)
KNOWN_LIBRARIES = {
    "jquery": ["jquery"],
    "bootstrap": ["bootstrap"],
    "react": ["react", "react-dom"],
    "vue": ["vue"],
    "angular": ["angular", "angular.js"],
    "lodash": ["lodash"],
    "moment": ["moment"],
    "axios": ["axios"],
    # add more over time...
}

# Per-library severity/risk defaults
LIB_RISKS = {
    "jquery": "Medium",
    "bootstrap": "Low",
    "react": "Low",
    "vue": "Low",
    "angular": "Medium",
    "lodash": "Low",
    "moment": "Medium",
    "axios": "Medium",
}

# Regex patterns to extract version from src url
SRC_VERSION_PATTERNS = [
    re.compile(r"@(?P<ver>\d+\.\d+\.\d+)"),             # .../library@1.2.3/...
    re.compile(r"-(?P<ver>\d+\.\d+\.\d+)(?:\.min)?\.js"), # library-1.2.3.min.js
    re.compile(r"/(?P<ver>\d+\.\d+\.\d+)/"),             # /1.2.3/ in path
    re.compile(r"[?&](?:ver|v)=?(?P<ver>\d+\.\d+\.\d+)") # ?v=1.2.3
]

# Regex to find version comments in head of script file
COMMENT_VERSION_PATTERNS = [
    re.compile(r"^\s*/\*\s*(?:version|ver|v)\s*[:=]?\s*(?P<ver>\d+\.\d+\.\d+)", re.I),
    re.compile(r"^\s*//\s*(?:version|ver|v)\s*[:=]?\s*(?P<ver>\d+\.\d+\.\d+)", re.I),
    re.compile(r"^\s*/\*\s*(?P<name>[A-Za-z0-9\-_\.]+)\s+v(?P<ver>\d+\.\d+\.\d+)", re.I),
]


async def fetch_text_head(session: aiohttp.ClientSession, url: str, max_bytes: int = 2048) -> str:
    """
    Fetch the first `max_bytes` bytes of a script (or page).
    Returns text or empty string on failure.
    """
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            # read only max_bytes to avoid downloading whole libs
            raw = await resp.content.read(max_bytes)
            try:
                return raw.decode(errors="replace")
            except Exception:
                return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


def infer_version_from_src(src: str) -> Optional[str]:
    for pat in SRC_VERSION_PATTERNS:
        m = pat.search(src)
        if m:
            return m.group("ver")
    return None


def infer_version_from_content(head: str) -> Optional[Tuple[str, str]]:
    """
    Return (name, version) if found in comment in head snippet, else None.
    """
    if not head:
        return None
    # check for comment patterns
    for pat in COMMENT_VERSION_PATTERNS:
        m = pat.search(head)
        if m:
            ver = m.groupdict().get("ver")
            name = m.groupdict().get("name")
            return (name or "", ver)
    return None


def guess_library_from_src(src: str) -> Optional[str]:
    """
    Try to guess library canonical name from src URL using KNOWN_LIBRARIES keys.
    """
    lower = src.lower()
    for canonical, keys in KNOWN_LIBRARIES.items():
        for key in keys:
            if key in lower:
                return canonical
    return None


async def query_cdnjs_latest(session: aiohttp.ClientSession, lib: str) -> Optional[str]:
    """
    Query cdnjs API for latest version of `lib`. Returns version string or None.
    API: https://api.cdnjs.com/libraries/<lib>?fields=latest
    """
    if not lib:
        return None
    url = f"https://api.cdnjs.com/libraries/{lib}?fields=version"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as resp:
            if resp.status == 200:
                data = await resp.json()
                # cdnjs returns 'version'
                return data.get("version")
    except Exception:
        pass
    return None


def compare_versions(found: Optional[str], latest: Optional[str]) -> str:
    """
    Very basic semver compare (supports x.y.z). Returns 'up-to-date', 'outdated', or 'unknown'.
    """
    if not found or not latest:
        return "unknown"
    def to_tuple(v: str):
        parts = v.split(".")
        return tuple(int(p) if p.isdigit() else 0 for p in (parts + ["0","0"])[:3])
    try:
        return "up-to-date" if to_tuple(found) >= to_tuple(latest) else "outdated"
    except Exception:
        return "unknown"


async def scan_frontend_libraries(page_url: str) -> Dict:
    """
    Main entry point. Returns standardized JSON result (see schema).
    """
    action = "frontend_libraries"
    results: List[Dict] = []
    # normalize url for fetching page
    if not page_url.startswith(("http://", "https://")):
        page_url = "https://" + page_url
    parsed = urlparse(page_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    timeout = aiohttp.ClientTimeout(total=15, connect=6)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # 1) fetch page HTML
        try:
            async with session.get(page_url) as resp:
                html = await resp.text()
        except Exception as e:
            return {
                "action": action,
                "target": page_url,
                "summary": {
                    "total_scripts": 0,
                    "unique_libraries": 0,
                    "with_detected_version": 0,
                    "without_detected_version": 0,
                    "up_to_date": 0,
                    "outdated": 0,
                    "unknown": 0,
                    "score": 0,
                    "risk_level": "High"
                },
                "general_recommendation": f"Could not fetch page HTML: {str(e)}",
                "results": []
            }

        # 2) extract script tags and inline scripts
        # simple regex to find <script ... src="..."> and inline <script>...</script>
        srcs = []
        for m in re.finditer(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\']', html, re.I):
            srcs.append(m.group(1).strip())

        # also capture inline script blocks (if we want to inspect head lines for versions)
        inline_scripts = []
        for m in re.finditer(r'<script\b[^>]*>(.*?)</script>', html, re.I | re.S):
            content = m.group(1).strip()
            if content:
                inline_scripts.append(content)

        # normalize src urls to absolute
        srcs_abs = [urljoin(base, s) for s in srcs]

        # dedupe
        srcs_abs = list(dict.fromkeys(srcs_abs))

        # 3) for each script src, attempt to detect library and version
        async def analyze_src(src_url: str):
            entry = {
                "source": src_url,
                "guesses": [],            # list of {"name","method"}
                "detected_version": None,
                "detected_name": None,
                "detection_methods": [],
                "raw_head": None
            }
            # guess name from src
            guessed = guess_library_from_src(src_url)
            if guessed:
                entry["detected_name"] = guessed
                entry["detection_methods"].append("src_guess")
                entry["guesses"].append({"name": guessed, "method": "src_guess"})

            # try to extract version from src URL
            ver = infer_version_from_src(src_url)
            if ver:
                entry["detected_version"] = ver
                entry["detection_methods"].append("src_url_regex")

            # fetch small head of script to look for version comments
            head = await fetch_text_head(session, src_url, max_bytes=2048)
            if head:
                entry["raw_head"] = head
                content_ver = infer_version_from_content(head)
                if content_ver:
                    name_from_comment, ver_from_comment = content_ver
                    # If name_from_comment is present, prefer it for detected_name
                    if name_from_comment:
                        entry["detected_name"] = name_from_comment.lower()
                        entry["detection_methods"].append("script_head_comment_name")
                    if ver_from_comment:
                        entry["detected_version"] = ver_from_comment
                        entry["detection_methods"].append("script_head_comment_version")

            return entry

        # run analyses with concurrency limit
        sem = asyncio.Semaphore(8)
        async def _sem_analyze(u):
            async with sem:
                return await analyze_src(u)

        tasks = [asyncio.create_task(_sem_analyze(s)) for s in srcs_abs]
        analyzed = await asyncio.gather(*tasks, return_exceptions=False)

        # additionally inspect inline scripts for version comments or identifiable names
        inline_detects = []
        for block in inline_scripts:
            head = block[:2000]
            content_ver = infer_version_from_content(head)
            if content_ver:
                name, ver = content_ver
                inline_detects.append({"name": name or None, "version": ver})

        # 4) aggregate by detected_name (or guess) to form library entries
        grouped = {}  # canonical_name or src -> entry
        for a in analyzed:
            name = a["detected_name"] or guess_library_from_src(a["source"]) or a["source"]
            key = name.lower() if isinstance(name, str) else a["source"]
            if key not in grouped:
                grouped[key] = {
                    "name": name if name and name != a["source"] else None,
                    "canonical": key if key in KNOWN_LIBRARIES else None,
                    "src_urls": [],
                    "detection_methods": [],
                    "detected_version": None,
                    "notes": []
                }
            g = grouped[key]
            g["src_urls"].append(a["source"])
            for m in a.get("detection_methods", []):
                if m not in g["detection_methods"]:
                    g["detection_methods"].append(m)
            if a.get("detected_version") and not g.get("detected_version"):
                g["detected_version"] = a["detected_version"]
            if a.get("raw_head"):
                # small heuristic: store sentinel that head had content
                g["notes"].append("script_head_snippet_present")

        # if inline detects found but not mapped, add them
        for idet in inline_detects:
            key = (idet["name"] or "inline").lower() if idet.get("name") else f"inline-{len(grouped)}"
            if key not in grouped:
                grouped[key] = {
                    "name": idet.get("name"),
                    "canonical": None,
                    "src_urls": [],
                    "detection_methods": ["inline_script_comment"],
                    "detected_version": idet.get("version"),
                    "notes": ["found_in_inline_script"]
                }
            else:
                if idet.get("version") and not grouped[key].get("detected_version"):
                    grouped[key]["detected_version"] = idet.get("version")
                if "inline_script_comment" not in grouped[key]["detection_methods"]:
                    grouped[key]["detection_methods"].append("inline_script_comment")

        # 5) query cdnjs for latest versions where possible
        # prepare session again (we still have `session`)
        results = []
        async def enrich_entry(k, data):
            name_candidate = (data["canonical"] or data["name"] or k)
            # try to query cdnjs using canonical or name_candidate
            latest = None
            # if canonical exists use that, else try name_candidate
            try_names = []
            if data.get("canonical"):
                try_names.append(data["canonical"])
            if data.get("name"):
                try_names.append(data["name"])
            try_names.append(k)
            # remove None and duplicates
            try_names = [t for i, t in enumerate(try_names) if t and t not in try_names[:i]]
            for tn in try_names:
                # query cdnjs
                latest = await query_cdnjs_latest(session, tn)
                if latest:
                    break

            status = "unknown"
            if data.get("detected_version"):
                status = compare_versions(data["detected_version"], latest) if latest else "unknown"
            else:
                status = "no-version"

            results_entry = {
                "name": data.get("name") or k,
                "canonical": data.get("canonical"),
                "src_urls": data.get("src_urls", []),
                "detection_methods": data.get("detection_methods", []),
                "detected_version": data.get("detected_version"),
                "latest_version": latest,
                "status": status,
                "risk": LIB_RISKS.get(data.get("canonical") or (data.get("name") or "").lower(), "Unknown"),
                "notes": data.get("notes", []),
                "recommendation": None
            }

            # generate recommendation
            if status == "outdated":
                results_entry["recommendation"] = f"Update {results_entry['name']} to {latest}."
            elif status == "up-to-date":
                results_entry["recommendation"] = "Library is up-to-date."
            elif status == "no-version":
                results_entry["recommendation"] = "No version detected — consider adding versioned assets or metadata."
            else:
                results_entry["recommendation"] = "Could not determine version or latest release."

            return results_entry

        # run enrichment concurrently
                # 5) query cdnjs for latest versions where possible
        tasks = [asyncio.create_task(enrich_entry(k, v)) for k, v in grouped.items()]
        all_results = await asyncio.gather(*tasks, return_exceptions=False)

        # 🔒 filter: only keep libraries with both detected and latest version
        results = [
            r for r in all_results
            if r.get("detected_version") and r.get("latest_version") and r.get("status") in ("up-to-date", "outdated")
        ]

        # 6) summary stats (based only on filtered results)
        total_scripts = len(srcs_abs) + len(inline_scripts)
        unique_libraries = len(results)
        with_ver = sum(1 for r in results if r.get("detected_version"))
        without_ver = 0  # filtered, so always 0
        up_to_date = sum(1 for r in results if r.get("status") == "up-to-date")
        outdated = sum(1 for r in results if r.get("status") == "outdated")
        unknown = 0  # filtered out

        # compute score (based on filtered)
        score = 100 if unique_libraries == 0 else int(((up_to_date) / max(1, unique_libraries)) * 100)
        if score >= 80:
            risk = "Low"
        elif score >= 50:
            risk = "Medium"
        else:
            risk = "High"

        return {
            "action": action,
            "target": page_url,
            "summary": {
                "total_scripts": total_scripts,
                "unique_libraries": unique_libraries,
                "with_detected_version": with_ver,
                "without_detected_version": without_ver,
                "up_to_date": up_to_date,
                "outdated": outdated,
                "unknown": unknown,
                "score": score,
                "risk_level": risk
            },
            "general_recommendation": (
                "Update outdated libraries immediately to reduce risks. "
                "Libraries marked 'up-to-date' are fine but should still be monitored for new releases."
            ),
            "results": results
        }
