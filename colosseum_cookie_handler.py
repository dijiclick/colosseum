"""
Cookie Handler for Colosseum.org - FIXED VERSION
=================================================
Properly handles cookies for both arena.colosseum.org and api.colosseum.org
"""

import json
from typing import List, Dict, Any
from time import time


def load_colosseum_cookies(filepath: str = r"C:\Users\Administrator\Desktop\colosseum crawler\colosium cookie.txt") -> List[Dict[str, Any]]:
    """
    Load cookies from JSON file and convert to Playwright format.
    Creates cookies for BOTH arena.colosseum.org and api.colosseum.org
    
    Args:
        filepath: Path to the cookies JSON file
        
    Returns:
        List of cookie dictionaries in Playwright format
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies_list = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Cookie file not found at {filepath}")
        print("   Please export cookies from your browser and save to this path.")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing cookie file: {e}")
        return []
    
    playwright_cookies = []
    current_time = time()
    
    # Important cookies we need for authentication
    important_cookies = ['sAccessToken', 'sFrontToken', 'st-last-access-token-update', '__vdpl']
    
    for cookie in cookies_list:
        domain = cookie.get("domain", "")
        name = cookie.get("name", "")
        
        # Filter for colosseum.org cookies
        if "colosseum.org" not in domain:
            continue
        
        # Check if expired
        expires = cookie.get("expirationDate")
        if expires and expires < current_time:
            print(f"⚠️  Warning: Cookie '{name}' has EXPIRED!")
            print(f"   Expired at: {expires}, Current time: {current_time}")
            print(f"   Please refresh your cookies from the browser!")
            continue
        
        # Create base cookie
        base_cookie = {
            "name": name,
            "value": cookie.get("value"),
            "path": cookie.get("path", "/"),
        }
        
        # Add optional fields
        if expires:
            base_cookie["expires"] = int(expires)
        
        if cookie.get("httpOnly") is not None:
            base_cookie["httpOnly"] = cookie.get("httpOnly")
        
        if cookie.get("secure") is not None:
            base_cookie["secure"] = cookie.get("secure")
        
        same_site = cookie.get("sameSite", "").lower()
        if same_site in ["strict", "lax", "none"]:
            base_cookie["sameSite"] = same_site.capitalize() if same_site != "none" else "None"
        
        # Create cookies for MULTIPLE domains
        # This is crucial because the API calls go to api.colosseum.org
        domains_to_set = ["arena.colosseum.org"]
        
        # For sAccessToken and sFrontToken, also add to API domain
        if name in important_cookies:
            domains_to_set.append("api.colosseum.org")
        
        for target_domain in domains_to_set:
            domain_cookie = base_cookie.copy()
            domain_cookie["domain"] = target_domain
            playwright_cookies.append(domain_cookie)
            print(f"  [Cookie] {name} -> {target_domain}")
    
    print(f"\n[OK] Loaded {len(playwright_cookies)} cookies for colosseum.org domains")
    
    # Warn if missing important cookies
    cookie_names = {c.get("name") for c in cookies_list}
    missing = [c for c in ['sAccessToken', 'sFrontToken'] if c not in cookie_names]
    if missing:
        print(f"\n⚠️  Warning: Missing important cookies: {missing}")
        print("   Authentication may fail without these cookies.")
    
    return playwright_cookies


def get_colosseum_headers() -> Dict[str, str]:
    """
    Return headers that mimic a real browser session.
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


def check_cookie_expiry(filepath: str = r"C:\Users\Administrator\Desktop\colosseum crawler\colosium cookie.txt") -> bool:
    """
    Check if cookies are still valid (not expired).
    
    Returns:
        True if cookies are valid, False if expired
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies_list = json.load(f)
    except:
        return False
    
    current_time = time()
    
    for cookie in cookies_list:
        if cookie.get("name") == "sAccessToken":
            expires = cookie.get("expirationDate")
            if expires:
                if expires < current_time:
                    remaining = 0
                else:
                    remaining = (expires - current_time) / 3600  # hours
                
                print(f"\n🔑 sAccessToken Status:")
                print(f"   Expires: {expires}")
                print(f"   Current: {current_time}")
                
                if remaining > 0:
                    print(f"   [OK] Valid for {remaining:.1f} more hours")
                    return True
                else:
                    print(f"   [EXPIRED]")
                    return False
    
    print("⚠️  Could not find sAccessToken in cookies")
    return False