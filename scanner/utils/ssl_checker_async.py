import httpx

async def check_hsts_enabled_async(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            hsts_header = response.headers.get("strict-transport-security")

        if hsts_header:
            return {
                "status": "PASS",
                "details": f"HSTS enabled: {hsts_header}"
            }
        else:
            return {
                "status": "FAIL",
                "details": "HSTS header not found"
            }

    except httpx.RequestError as e:
        return {
            "status": "FAIL",
            "details": f"Request error during HSTS check: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "details": f"Unexpected error checking HSTS: {str(e)}"
        }

import asyncio
from .ssl_checker import check_ssl_validity, check_ssl_protocols

async def check_ssl_validity_async(url):
    return await asyncio.to_thread(check_ssl_validity, url)

async def check_ssl_protocols_async(url):
    return await asyncio.to_thread(check_ssl_protocols, url)
