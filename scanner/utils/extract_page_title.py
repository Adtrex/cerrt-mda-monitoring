import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def get_page_title(url, timeout=10):
    """
    Fetch the page title from a URL.
    
    Args:
        url: The URL to fetch the title from
        timeout: Request timeout in seconds (default: 10)
        
    Returns:
        str: The page title or None if not found
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, verify=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to get title
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            return clean_title(title)
        
        # Fallback: try og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return clean_title(og_title['content'])
        
        # Fallback: try twitter:title meta tag
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return clean_title(twitter_title['content'])
        
        # Fallback: try first h1
        h1 = soup.find('h1')
        if h1 and h1.get_text():
            return clean_title(h1.get_text())
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page title: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def clean_title(title):
    """
    Clean up the title by removing extra whitespace and common suffixes.
    
    Args:
        title: Raw title string
        
    Returns:
        str: Cleaned title
    """
    if not title:
        return None
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Optionally remove common separators and suffixes (uncomment if needed)
    # Common patterns: "Page Title | Site Name" or "Page Title - Site Name"
    # title = re.split(r'\s+[-|–—]\s+', title)[0]
    
    return title


def get_company_name_from_title(url, timeout=10):
    """
    Extract company/brand name from page title.
    Often the company name appears after a separator in the title.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        str: Company name or full title if separator not found
    """
    try:
        title = get_page_title(url, timeout)
        if not title:
            return None
        
        # Common separators: | - – — ::
        separators = [' | ', ' - ', ' – ', ' — ', ' :: ', ' | ']
        
        for sep in separators:
            if sep in title:
                parts = title.split(sep)
                # Usually company name is the last part
                company = parts[-1].strip()
                if company:
                    return company
        
        # No separator found, return full title
        return title
        
    except Exception as e:
        print(f"Error extracting company name: {e}")
        return None


def get_domain_and_title(url, timeout=10):
    """
    Get both domain name and page title.
    
    Args:
        url: The URL to analyze
        timeout: Request timeout in seconds
        
    Returns:
        dict: {'domain': str, 'title': str, 'company': str}
    """
    try:
        # Extract domain
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        # Get title
        title = get_page_title(url, timeout)
        
        # Try to extract company name
        company = get_company_name_from_title(url, timeout)
        
        return {
            'domain': domain,
            'title': title,
            'company': company
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'domain': None,
            'title': None,
            'company': None
        }


# Example usage
if __name__ == "__main__":
    test_url = "https://www.example.com"
    
    # Simple title extraction
    title = get_page_title(test_url)
    print(f"Page Title: {title}")
    
    # Company name extraction
    company = get_company_name_from_title(test_url)
    print(f"Company Name: {company}")
    
    # Get all info
    info = get_domain_and_title(test_url)
    print(f"Domain: {info['domain']}")
    print(f"Title: {info['title']}")
    print(f"Company: {info['company']}")