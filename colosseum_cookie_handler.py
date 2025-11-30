"""
Cookie Handler for Colosseum.org
Loads browser cookies and converts them to Playwright format for authenticated requests.
"""

import json
from typing import List, Dict, Any
from datetime import datetime


def load_colosseum_cookies(filepath: str = r"c:\Users\ariad\OneDrive\Desktop\colosium cookie.txt") -> List[Dict[str, Any]]:
    """
    Load cookies from JSON file (exported from browser) and convert to Playwright format.
    
    Args:
        filepath: Path to the cookies JSON file
        
    Returns:
        List of cookie dictionaries in Playwright format
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies_list = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Cookie file not found at {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing cookie file: {e}")
        return []
    
    # Filter only colosseum.org cookies and convert to Playwright format
    playwright_cookies = []
    
    for cookie in cookies_list:
        domain = cookie.get("domain", "")
        
        # Filter for colosseum.org domains
        if "colosseum.org" not in domain:
            continue
        
        # Convert to Playwright format
        # For Playwright add_cookies, we need to use the exact subdomain (arena.colosseum.org)
        # Parent domain cookies (.colosseum.org) should be set for arena.colosseum.org
        cookie_domain = "arena.colosseum.org"  # Always use arena.colosseum.org for Playwright
        
        playwright_cookie = {
            "name": cookie.get("name"),
            "value": cookie.get("value"),
            "domain": cookie_domain,
            "path": cookie.get("path", "/"),
        }
        
        # Add optional fields if present
        if cookie.get("expirationDate"):
            # Playwright uses seconds since epoch
            expires = cookie.get("expirationDate")
            if expires:
                # Check if expired
                from time import time
                current_time = time()
                if expires < current_time:
                    print(f"Warning: Cookie {cookie.get('name')} is expired")
                else:
                    playwright_cookie["expires"] = int(expires)
        
        if cookie.get("httpOnly") is not None:
            playwright_cookie["httpOnly"] = cookie.get("httpOnly")
        
        if cookie.get("secure") is not None:
            playwright_cookie["secure"] = cookie.get("secure")
        
        same_site = cookie.get("sameSite", "").lower()
        if same_site in ["strict", "lax", "none"]:
            # Playwright expects capitalized: Strict, Lax, None
            playwright_cookie["sameSite"] = same_site.capitalize() if same_site != "none" else "None"
        
        playwright_cookies.append(playwright_cookie)
        print(f"  Cookie: {cookie.get('name')} -> {cookie_domain}")
    
    print(f"Loaded {len(playwright_cookies)} cookies for colosseum.org")
    return playwright_cookies


def get_colosseum_headers() -> Dict[str, str]:
    """
    Return headers that mimic a real browser session.
    This helps avoid being blocked as a bot.
    
    Returns:
        Dictionary of HTTP headers
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

