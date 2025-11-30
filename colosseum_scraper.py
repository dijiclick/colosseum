"""
Web Scraper for Colosseum.org Profiles
Uses Playwright to navigate, click profiles, and extract comprehensive profile data.
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time
import re
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin

from colosseum_cookie_handler import load_colosseum_cookies, get_colosseum_headers


class ColosseumScraper:
    """Main scraper class using Playwright for browser automation"""
    
    def __init__(self, cookies_file: str = r"c:\Users\ariad\OneDrive\Desktop\colosium cookie.txt", headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            cookies_file: Path to cookies JSON file
            headless: Whether to run browser in headless mode
        """
        self.cookies_file = cookies_file
        self.headless = headless
        self.base_url = "https://arena.colosseum.org"
        self.profiles_url = f"{self.base_url}/profiles"
        self.request_delay = 2  # seconds between requests
        self.max_retries = 3
        
        # Will be initialized in start()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def start(self):
        """Start the browser and load cookies."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)  # Always run headless
        
        # Load cookies first
        cookies = load_colosseum_cookies(self.cookies_file)
        
        # Create context with cookies
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=get_colosseum_headers().get("User-Agent")
        )
        
        self.page = self.context.new_page()
        
        if cookies:
            # Navigate to the domain first so cookies can be set
            print("Setting up authentication...")
            self.page.goto("https://arena.colosseum.org", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            
            # Add cookies to the context (must be done after navigating to the domain)
            try:
                # Add cookies for arena.colosseum.org
                self.context.add_cookies(cookies)
                print(f"Added {len(cookies)} cookies to context")
                
                # Also add cookies for api.colosseum.org (API domain)
                api_cookies = []
                for cookie in cookies:
                    api_cookie = cookie.copy()
                    # Set domain to api.colosseum.org for API calls
                    api_cookie['domain'] = 'api.colosseum.org'
                    api_cookies.append(api_cookie)
                
                try:
                    self.context.add_cookies(api_cookies)
                    print(f"Also added {len(api_cookies)} cookies for API domain")
                except Exception as e:
                    print(f"Note: Could not add cookies for API domain: {e}")
                
                # Verify cookies were added
                context_cookies = self.context.cookies()
                print(f"Context now has {len(context_cookies)} cookies:")
                for c in context_cookies[:5]:  # Show first 5
                    print(f"  - {c['name']} for {c.get('domain', 'N/A')}")
                
            except Exception as e:
                print(f"Error adding cookies: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Navigate to home page to verify authentication
            print("Verifying authentication...")
            self.page.goto("https://arena.colosseum.org", wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)
            
            # Check if we're logged in (not redirected to signup)
            current_url = self.page.url
            print(f"Current URL after auth: {current_url}")
            if "signup" in current_url.lower() or "login" in current_url.lower():
                print("Warning: Redirected to signup/login - cookies may be invalid or expired")
                # Try one more time with a fresh navigation
                self.page.goto("https://arena.colosseum.org/profiles", wait_until="domcontentloaded", timeout=60000)
                time.sleep(3)
                if "signup" in self.page.url.lower():
                    print("Authentication failed - please check if cookies are still valid")
            else:
                print("Authentication successful!")
        else:
            print("Warning: No cookies loaded")
    
    def stop(self):
        """Close the browser."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("Browser closed")
    
    def navigate_to_profiles(self) -> bool:
        """
        Navigate to the profiles page.
        
        Returns:
            True if successful
        """
        try:
            print(f"Navigating to {self.profiles_url}...")
            
            # Set up request interception to see API calls
            api_responses = []
            
            def handle_response(response):
                url = response.url
                if 'api' in url.lower() or 'profile' in url.lower() or response.request.resource_type == 'xhr':
                    api_responses.append({
                        'url': url,
                        'status': response.status,
                        'method': response.request.method
                    })
            
            self.page.on('response', handle_response)
            
            # Use "domcontentloaded" instead of "networkidle" for faster loading
            self.page.goto(self.profiles_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)  # Wait for API calls
            
            # Print API calls we found
            if api_responses:
                print(f"Found {len(api_responses)} API calls:")
                for resp in api_responses[:5]:  # Show first 5
                    print(f"  {resp['method']} {resp['url']} ({resp['status']})")
            
            # Check if we're on the profiles page
            current_url = self.page.url
            if "profiles" in current_url.lower() or "arena.colosseum.org" in current_url.lower():
                print("Successfully navigated to profiles page")
                return True
            else:
                print(f"Warning: May not be on profiles page. Current URL: {current_url}")
                return False
        except Exception as e:
            print(f"Error navigating to profiles page: {e}")
            return False
    
    def get_profile_cards(self) -> List[Dict[str, Any]]:
        """
        Extract profile cards from the listing page.
        
        Returns:
            List of profile card data dictionaries
        """
        profile_cards = []
        
        try:
            # Wait for loading spinner to disappear and content to load
            print("Waiting for profiles to load...")
            
            # Wait for network to be idle (API calls to complete)
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except:
                pass
            
            # Wait for spinner to disappear
            try:
                self.page.wait_for_selector('.animate-spin', state='hidden', timeout=10000)
            except:
                pass
            
            # Wait a bit more for content to render
            time.sleep(3)
            
            # Try scrolling to trigger lazy loading
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            # Try waiting for any profile-related content
            try:
                # Wait for any text containing @ symbol (usernames) or profile cards
                self.page.wait_for_function(
                    'document.body.innerText.includes("@") || document.querySelectorAll("[class*=\'profile\'], [class*=\'card\'], article").length > 0',
                    timeout=20000
                )
            except:
                pass
            
            # One more wait for rendering
            time.sleep(2)
            
            # Try interacting with search to trigger profile load
            # The page might need a search query or just focus on the search input
            try:
                search_input = self.page.query_selector('input[placeholder*="Search"], input[placeholder*="Role"], #profileSearchInput')
                if search_input:
                    print("Found search input, trying to trigger profile load...")
                    search_input.click()
                    time.sleep(1)
                    # Try typing something or just pressing enter
                    search_input.press('Enter')
                    time.sleep(3)
            except Exception as e:
                print(f"Could not interact with search: {e}")
            
            # Get page content to debug
            try:
                page_text = self.page.inner_text('body')
            except:
                page_text = ""
            page_html = self.page.content()
            
            # Try multiple selectors to find profile cards
            # Based on the image, profiles are in a grid layout
            selectors = [
                'div[class*="profile"]',
                'div[class*="card"]',
                'div[class*="Profile"]',
                'div[class*="Card"]',
                'article',
                '[data-testid*="profile"]',
                '[data-testid*="Profile"]',
                'a[href*="/profile"]',
                'a[href*="/profiles"]',
                'div[class*="user"]',
                'div[class*="User"]',
                '[role="article"]',
                'div[class*="grid"] > div',
                'div[class*="Grid"] > div'
            ]
            
            cards = None
            for selector in selectors:
                try:
                    cards = self.page.query_selector_all(selector)
                    if cards and len(cards) > 2:  # Need at least a few to be valid
                        print(f"Found {len(cards)} elements with selector: {selector}")
                        break
                except:
                    continue
            
            if not cards or len(cards) == 0:
                # Try to find elements containing @ symbols (usernames)
                print("Trying to find elements with @ symbols (usernames)...")
                all_elements = self.page.query_selector_all('div, article, a')
                cards_with_at = []
                for elem in all_elements:
                    try:
                        text = elem.inner_text()
                        if '@' in text and len(text) < 500:  # Likely a profile card
                            cards_with_at.append(elem)
                    except:
                        continue
                if cards_with_at:
                    cards = cards_with_at
                    print(f"Found {len(cards)} elements containing @ symbols")
            
            if not cards or len(cards) == 0:
                print("Could not find profile cards using selectors.")
                # Try to save page HTML for debugging
                try:
                    with open('debug_page.html', 'w', encoding='utf-8') as f:
                        f.write(page_html)
                    print("Saved page HTML to debug_page.html for inspection")
                except:
                    pass
                return []
            
            print(f"Found {len(cards)} potential profile elements")
            
            # Extract basic info from each card
            for i, card in enumerate(cards[:100]):  # Limit to first 100
                try:
                    card_data = self._extract_card_info(card, i)
                    if card_data and card_data.get("username"):
                        profile_cards.append(card_data)
                except Exception as e:
                    continue  # Silently skip errors
            
            print(f"Extracted {len(profile_cards)} profile cards")
            return profile_cards
            
        except Exception as e:
            print(f"Error getting profile cards: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _clean_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove internal fields that shouldn't be saved to database."""
        cleaned = data.copy()
        # Remove internal fields
        cleaned.pop('card_index', None)
        return cleaned
    
    def _extract_card_info(self, card_element, index: int) -> Optional[Dict[str, Any]]:
        """
        Extract basic information from a profile card element.
        
        Args:
            card_element: Playwright element handle
            index: Index of the card
            
        Returns:
            Dictionary with card data or None
        """
        try:
            # Get text content
            text = card_element.inner_text() if hasattr(card_element, 'inner_text') else ""
            html = card_element.inner_html() if hasattr(card_element, 'inner_html') else ""
            
            # Try to extract username (starts with @)
            username_match = re.search(r'@(\w+)', text)
            username = f"@{username_match.group(1)}" if username_match else None
            
            # Try to extract display name (usually the first line or bold text)
            display_name = None
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                # First non-empty line that's not a username
                for line in lines:
                    if not line.startswith('@') and len(line) > 1 and len(line) < 50:
                        display_name = line
                        break
            
            # Extract tags (usually prefixed with #)
            tags = re.findall(r'#\s*([A-Z\s]+)', text)
            tags = [tag.strip() for tag in tags if tag.strip()]
            
            # Extract location (look for common patterns)
            location = None
            location_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # City names
            ]
            for pattern in location_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # Filter out common false positives
                    false_positives = ['PRODUCT', 'MANAGER', 'DESIGNER', 'DEVELOPER', 'ENGINEER']
                    for match in matches:
                        if match not in false_positives and len(match) > 2:
                            location = match
                            break
                    if location:
                        break
            
            # Extract languages
            languages = []
            if 'English' in text:
                languages.append('English')
            if 'Spanish' in text:
                languages.append('Spanish')
            if 'Japanese' in text:
                languages.append('Japanese')
            if 'Russian' in text:
                languages.append('Russian')
            if 'Yoruba' in text:
                languages.append('Yoruba')
            
            # Extract description (usually a short sentence)
            description = None
            # Look for text that's not a tag, username, or location
            description_lines = [line.strip() for line in text.split('\n') 
                               if line.strip() and not line.startswith('#') 
                               and not line.startswith('@') 
                               and line != display_name
                               and line != location
                               and len(line) > 10 and len(line) < 200]
            if description_lines:
                description = description_lines[0]
            
            if not username:
                return None
            
            return {
                "username": username,
                "display_name": display_name,
                "tags": tags,
                "description": description,
                "location": location,
                "languages": languages,
                "card_index": index
            }
            
        except Exception as e:
            print(f"    Error extracting card info: {e}")
            return None
    
    def click_profile_and_extract_details(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Click on a profile card and extract detailed information.
        
        Args:
            card_data: Basic card data
            
        Returns:
            Complete profile data with details
        """
        profile_data = card_data.copy()
        
        try:
            # Try to find and click the profile card
            # First, try to find element by username or display name
            username = card_data.get("username", "").replace("@", "")
            display_name = card_data.get("display_name", "")
            
            clicked = False
            
            # Try multiple strategies to click the profile
            click_strategies = [
                # Strategy 1: Click by text content
                lambda: self.page.click(f'text={display_name}', timeout=5000) if display_name else False,
                lambda: self.page.click(f'text={username}', timeout=5000) if username else False,
                # Strategy 2: Click by link
                lambda: self.page.click(f'a[href*="{username}"]', timeout=5000) if username else False,
                # Strategy 3: Click by data attribute
                lambda: self.page.click(f'[data-username="{username}"]', timeout=5000) if username else False,
            ]
            
            for strategy in click_strategies:
                try:
                    if strategy():
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                # Fallback: try clicking on the card element directly
                # We'll need to re-find it
                try:
                    # Scroll to make sure element is visible
                    self.page.evaluate(f'document.querySelectorAll("a, div, button").forEach(el => {{ if (el.innerText.includes("{display_name}") || el.innerText.includes("{username}")) {{ el.scrollIntoView(); }} }})')
                    time.sleep(0.5)
                    
                    # Try clicking by text
                    if display_name:
                        self.page.click(f'text={display_name}', timeout=3000)
                        clicked = True
                except:
                    pass
            
            if clicked:
                # Wait for detail modal/view to appear
                time.sleep(2)
                
                # Extract detailed information
                details = self._extract_profile_details()
                profile_data.update(details)
                
                # Close modal if it exists
                self._close_profile_modal()
                
                time.sleep(self.request_delay)
            else:
                print(f"    Could not click profile for {username}")
            
        except Exception as e:
            print(f"    Error clicking profile {card_data.get('username')}: {e}")
        
        return profile_data
    
    def _extract_profile_details(self) -> Dict[str, Any]:
        """
        Extract detailed information from the profile detail view/modal.
        
        Returns:
            Dictionary with detailed profile data
        """
        details = {
            "company": None,
            "looking_for_teammates": False,
            "project_description": None,
            "i_am_a_roles": [],
            "looking_for_roles": [],
            "interested_in_topics": [],
            "about": None,
            "avatar_url": None,
            "profile_url": None
        }
        
        try:
            # Get page content
            page_text = self.page.inner_text('body')
            page_html = self.page.content()
            
            # Extract company (usually after briefcase icon or in header)
            company_patterns = [
                r'LOOP',
                r'@\s*([A-Z][a-zA-Z]+)',  # Company after @
                r'Co-Founder\s+@\s*([A-Z][a-zA-Z]+)',
                r'founder\s+&?\s*engr\s+@([a-z]+)',
            ]
            for pattern in company_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    details["company"] = match.group(1) if match.lastindex else match.group(0)
                    break
            
            # Check if "Looking for teammates" section exists
            if "LOOKING FOR TEAMMATES" in page_text.upper() or "LOOKING FOR" in page_text.upper():
                details["looking_for_teammates"] = True
                
                # Extract project description
                # Usually after "LOOKING FOR TEAMMATES" heading
                teammates_section = re.search(r'LOOKING FOR TEAMMATES[^\n]*\n([^\n]+)', page_text, re.IGNORECASE)
                if teammates_section:
                    details["project_description"] = teammates_section.group(1).strip()
                
                # Extract "I AM A" roles
                i_am_a_match = re.search(r'I AM A[^\n]*\n((?:#[^\n]+\n?)+)', page_text, re.IGNORECASE)
                if i_am_a_match:
                    roles_text = i_am_a_match.group(1)
                    details["i_am_a_roles"] = re.findall(r'#\s*([A-Z\s/]+)', roles_text)
                    details["i_am_a_roles"] = [r.strip() for r in details["i_am_a_roles"]]
                
                # Extract "LOOKING FOR" roles
                looking_for_match = re.search(r'LOOKING FOR[^\n]*\n((?:#[^\n]+\n?)+)', page_text, re.IGNORECASE)
                if looking_for_match:
                    roles_text = looking_for_match.group(1)
                    details["looking_for_roles"] = re.findall(r'#\s*([A-Z\s/]+)', roles_text)
                    details["looking_for_roles"] = [r.strip() for r in details["looking_for_roles"]]
                
                # Extract "INTERESTED IN" topics
                interested_match = re.search(r'INTERESTED IN[^\n]*\n((?:#[^\n]+\n?)+)', page_text, re.IGNORECASE)
                if interested_match:
                    topics_text = interested_match.group(1)
                    details["interested_in_topics"] = re.findall(r'#\s*([A-Z\s/]+)', topics_text)
                    details["interested_in_topics"] = [t.strip() for t in details["interested_in_topics"]]
            
            # Extract "ABOUT" section
            about_match = re.search(r'ABOUT[^\n]*\n([^\n]+(?:\n[^\n]+)*)', page_text, re.IGNORECASE)
            if about_match:
                details["about"] = about_match.group(1).strip()
            
            # Extract avatar URL
            try:
                avatar_img = self.page.query_selector('img[src*="avatar"], img[class*="avatar"], img[alt*="profile"]')
                if avatar_img:
                    details["avatar_url"] = avatar_img.get_attribute('src')
            except:
                pass
            
            # Get current URL as profile URL
            details["profile_url"] = self.page.url
            
        except Exception as e:
            print(f"    Error extracting profile details: {e}")
        
        return details
    
    def _close_profile_modal(self):
        """Close the profile modal if it's open."""
        try:
            # Try to find and click close button (X button)
            close_selectors = [
                'button[aria-label*="close" i]',
                'button[aria-label*="Close" i]',
                '[class*="close"]',
                '[class*="Close"]',
                'button:has-text("×")',
                'button:has-text("X")',
                '[data-testid*="close"]'
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = self.page.query_selector(selector)
                    if close_btn:
                        close_btn.click()
                        time.sleep(0.5)
                        return
                except:
                    continue
            
            # Try pressing Escape key
            self.page.keyboard.press('Escape')
            time.sleep(0.5)
            
        except Exception as e:
            # Ignore errors when closing modal
            pass
    
    def scrape_all_profiles(self, existing_usernames: set = None, max_profiles: int = None) -> List[Dict[str, Any]]:
        """
        Scrape all profiles from the profiles page.
        
        Args:
            existing_usernames: Set of usernames to skip
            max_profiles: Maximum number of profiles to scrape (None for all)
            
        Returns:
            List of complete profile data dictionaries
        """
        if existing_usernames is None:
            existing_usernames = set()
        
        profiles = []
        
        # Navigate to profiles page
        if not self.navigate_to_profiles():
            return profiles
        
        # Get all profile cards
        profile_cards = self.get_profile_cards()
        
        # Limit to max_profiles if specified
        if max_profiles and len(profile_cards) > max_profiles:
            profile_cards = profile_cards[:max_profiles]
            print(f"\nLimited to {max_profiles} profiles")
        
        print(f"\nFound {len(profile_cards)} profiles to scrape")
        print(f"Skipping {len([c for c in profile_cards if c.get('username') in existing_usernames])} existing profiles\n")
        
        # Process each profile
        for i, card_data in enumerate(profile_cards, 1):
            username = card_data.get("username")
            
            if username in existing_usernames:
                print(f"[{i}/{len(profile_cards)}] Skipping existing: {username}")
                continue
            
            print(f"[{i}/{len(profile_cards)}] Processing: {username}")
            
            try:
                # Click and get details
                complete_profile = self.click_profile_and_extract_details(card_data)
                
                # Clean the data (remove internal fields)
                complete_profile = self._clean_profile_data(complete_profile)
                
                # Add source URL
                complete_profile["source_url"] = self.profiles_url
                
                profiles.append(complete_profile)
                print(f"  [OK] Extracted data for {username}")
                
            except Exception as e:
                print(f"  [ERROR] Error processing {username}: {e}")
                continue
        
        return profiles

