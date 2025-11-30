"""
Web Scraper for Colosseum.org Profiles - FIXED VERSION with Profile Click Support
==================================================================================
Key fixes:
1. Properly clicks profile cards to open the side panel
2. Waits for side panel to load with detailed profile info
3. Extracts complete profile data from the side panel
4. Handles closing/navigating between profiles
"""

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time
import re
import json
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
        
        # Store intercepted API data
        self.api_profiles = []
        self.api_responses = []
        
        # Will be initialized in start()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    def _handle_response(self, response):
        """Handle intercepted responses to capture profile API data."""
        url = response.url
        
        # Look for profile-related API calls
        if any(keyword in url.lower() for keyword in ['profile', 'collaborator', 'member', 'user', 'search']):
            if 'api' in url.lower() or response.request.resource_type in ['xhr', 'fetch']:
                try:
                    status = response.status
                    if status == 200:
                        try:
                            data = response.json()
                            self.api_responses.append({
                                'url': url,
                                'status': status,
                                'data': data
                            })
                            
                            # Extract profiles from response
                            profiles = None
                            if isinstance(data, list):
                                profiles = data
                            elif isinstance(data, dict):
                                for key in ['data', 'profiles', 'results', 'items', 'users', 'members']:
                                    if key in data and isinstance(data[key], list):
                                        profiles = data[key]
                                        break
                            
                            if profiles:
                                print(f"  [API] Intercepted {len(profiles)} profiles from API: {url[:80]}...")
                                self.api_profiles.extend(profiles)
                        except:
                            pass
                except Exception as e:
                    pass
    
    def start(self):
        """Start the browser and load cookies."""
        self.playwright = sync_playwright().start()
        
        # Use headed mode for debugging if needed
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        # Load cookies first
        cookies = load_colosseum_cookies(self.cookies_file)
        
        # Create context with cookies
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        # Add cookies to context
        if cookies:
            self.context.add_cookies(cookies)
            print(f"Added {len(cookies)} cookies to browser context")
        
        # Create page
        self.page = self.context.new_page()
        
        # Set up response interception BEFORE navigation
        self.page.on('response', self._handle_response)
        
        print("Browser started successfully")
    
    def stop(self):
        """Stop the browser."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("Browser stopped")
    
    def navigate_to_profiles(self) -> bool:
        """
        Navigate to the profiles page and wait for it to load.
        
        Returns:
            True if navigation successful
        """
        try:
            print(f"\nNavigating to {self.profiles_url}")
            
            # Clear any previous API data
            self.api_profiles = []
            self.api_responses = []
            
            # Navigate with a longer timeout
            self.page.goto(self.profiles_url, wait_until="networkidle", timeout=60000)
            
            print("Page loaded, waiting for content...")
            
            # Wait for the page to be ready
            time.sleep(3)
            
            # Wait for profile cards to appear
            # Profile cards are buttons with specific structure
            max_wait = 30
            for _ in range(max_wait):
                # Check if we have API data
                if self.api_profiles:
                    print(f"Got {len(self.api_profiles)} profiles from API")
                    break
                
                # Check for spinner (loading state)
                try:
                    spinner = self.page.query_selector('.animate-spin')
                    if not spinner or not spinner.is_visible():
                        print("Spinner disappeared")
                        break
                except:
                    pass
                
                # Check for profile cards in DOM
                try:
                    # Profile cards are buttons inside the grid
                    cards = self.page.query_selector_all('button.border-gray-dark-6')
                    if len(cards) > 0:
                        print(f"Found {len(cards)} profile card buttons")
                        break
                except:
                    pass
                
                time.sleep(1)
            
            # Additional wait for any late API calls
            time.sleep(3)
            
            # Print what we found
            print(f"\nAPI Interception Summary:")
            print(f"  - Total API responses captured: {len(self.api_responses)}")
            print(f"  - Profiles from API: {len(self.api_profiles)}")
            
            # Check if we're on the profiles page
            current_url = self.page.url
            if "profiles" in current_url.lower():
                print("[OK] Successfully on profiles page")
                return True
            else:
                print(f"Warning: May not be on profiles page. Current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error navigating to profiles page: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_profile_card_elements(self) -> List:
        """
        Get all clickable profile card elements from the page.
        
        Returns:
            List of Playwright element handles for profile cards
        """
        # Profile cards are button elements with this class pattern
        # They're in a grid: div.gap-lg.grid.grid-cols-1.md:grid-cols-2
        
        selectors = [
            'button.border-gray-dark-6',  # Main card button
            'div.gap-lg.grid button',      # Buttons in grid
            'main button[class*="border"][class*="rounded"]',  # Fallback
        ]
        
        for selector in selectors:
            try:
                cards = self.page.query_selector_all(selector)
                # Filter to only visible profile cards (they contain username with @)
                profile_cards = []
                for card in cards:
                    try:
                        text = card.inner_text()
                        if '@' in text and card.is_visible():
                            profile_cards.append(card)
                    except:
                        continue
                
                if profile_cards:
                    print(f"Found {len(profile_cards)} profile cards using selector: {selector}")
                    return profile_cards
            except Exception as e:
                continue
        
        print("No profile cards found with any selector")
        return []
    
    def extract_basic_info_from_card(self, card_element) -> Dict[str, Any]:
        """
        Extract basic profile info from a card element.
        
        Args:
            card_element: Playwright element handle for the card
            
        Returns:
            Dictionary with basic profile info
        """
        profile = {
            "username": None,
            "display_name": None,
            "description": None,
            "location": None,
            "tags": [],
            "languages": [],
            "company": None,
        }
        
        try:
            text = card_element.inner_text()
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            # Find username (starts with @)
            for line in lines:
                if line.startswith('@'):
                    profile['username'] = line
                    break
            
            # Find display name (usually the line before @username)
            for i, line in enumerate(lines):
                if line.startswith('@') and i > 0:
                    profile['display_name'] = lines[i-1]
                    break
            
            # Extract tags (look for role tags like "Product Manager", "Software Engineer")
            role_keywords = ['manager', 'developer', 'designer', 'engineer', 'marketer', 
                           'founder', 'creator', 'ops', 'biz dev', 'lawyer']
            for line in lines:
                if any(kw in line.lower() for kw in role_keywords):
                    # Skip if it's a number like "+5"
                    if not line.startswith('+'):
                        profile['tags'].append(line)
            
            # Extract location (look for city names pattern)
            # Location usually comes after work/company info
            for i, line in enumerate(lines):
                # Location lines are usually short and don't have # or @
                if len(line) < 30 and not line.startswith(('#', '@', '+')) and \
                   not any(kw in line.lower() for kw in role_keywords):
                    # Could be location or company
                    if i > len(lines) // 2:  # Usually in second half
                        if not profile['location']:
                            profile['location'] = line
            
            # Extract languages
            language_keywords = ['english', 'spanish', 'chinese', 'japanese', 'russian', 
                               'portuguese', 'french', 'german', 'korean', 'hindi',
                               'arabic', 'indonesian', 'italian', 'turkish', 'vietnamese']
            for line in lines:
                for lang in language_keywords:
                    if lang in line.lower():
                        # Parse comma-separated languages
                        langs = [l.strip() for l in line.split(',')]
                        profile['languages'].extend(langs)
                        break
            
        except Exception as e:
            print(f"Error extracting basic info: {e}")
        
        return profile
    
    def click_profile_and_extract_details(self, card_element, card_index: int) -> Dict[str, Any]:
        """
        Click on a profile card and extract detailed information from the side panel.
        
        Args:
            card_element: Playwright element handle for the card
            card_index: Index of the card (for logging)
            
        Returns:
            Dictionary with complete profile data
        """
        # First extract basic info from the card itself
        profile = self.extract_basic_info_from_card(card_element)
        profile['card_index'] = card_index
        
        try:
            # First, close any existing modal/overlay
            try:
                # Check for overlay and close it
                overlay = self.page.query_selector('div[class*="fixed"][class*="inset-0"][class*="bg-black"]')
                if overlay and overlay.is_visible():
                    self.page.keyboard.press('Escape')
                    time.sleep(0.5)
            except:
                pass
            
            # Scroll the card into view first
            try:
                card_element.scroll_into_view_if_needed()
                time.sleep(0.3)
            except:
                pass
            
            # Click the card to open the side panel
            print(f"    Clicking profile card...")
            
            # Try multiple click strategies
            clicked = False
            try:
                # Strategy 1: Direct click
                card_element.click(timeout=5000)
                clicked = True
            except:
                try:
                    # Strategy 2: Force click (bypasses actionability checks)
                    card_element.click(force=True, timeout=3000)
                    clicked = True
                except:
                    try:
                        # Strategy 3: Click using JavaScript
                        self.page.evaluate('(element) => element.click()', card_element)
                        clicked = True
                    except:
                        pass
            
            if not clicked:
                print("    Could not click card, trying to extract from API data")
                return profile
            
            # Wait for side panel to populate with content
            # The right panel is a persistent sidebar that gets populated on click
            time.sleep(1.5)
            
            # Look for the right sidebar panel - it's always visible but gets populated
            # Check multiple selectors for the right panel
            panel_selectors = [
                'aside.xl\\:block',  # Right sidebar (escaped colon for CSS selector)
                'aside:has-text("VIEW")',  # Aside with VIEW PROFILE text
                'aside:has-text("@")',  # Aside with username
                'div[class*="sticky"][class*="top"]',  # Sticky sidebar
                'div[class*="w-1/4"]',  # Right column (1/4 width)
            ]
            
            panel_found = False
            panel = None
            
            for selector in panel_selectors:
                try:
                    # Wait a bit for content to load
                    time.sleep(0.5)
                    panel = self.page.query_selector(selector)
                    if panel:
                        text = panel.inner_text().strip()
                        # Check if it has meaningful content (not just empty)
                        if text and len(text) > 50 and ('@' in text or 'VIEW' in text.upper()):
                            panel_found = True
                            print(f"    Right panel found with content ({len(text)} chars)")
                            break
                except Exception as e:
                    continue
            
            if not panel_found:
                # Try checking all aside elements
                try:
                    all_asides = self.page.query_selector_all('aside')
                    for aside in all_asides:
                        text = aside.inner_text().strip()
                        if text and len(text) > 50:
                            panel = aside
                            panel_found = True
                            print(f"    Found aside with content ({len(text)} chars)")
                            break
                except:
                    pass
            
            if not panel_found:
                print("    Right panel did not populate with content")
                # Don't return early - try to extract anyway in case content is there
            
            # Now extract detailed info from the side panel
            detailed_info = self._extract_side_panel_info()
            
            # Merge detailed info into profile
            for key, value in detailed_info.items():
                if value:  # Only override if we got actual data
                    profile[key] = value
            
            # No need to close the panel - it's a persistent sidebar
            # Just wait a moment before moving to next profile
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error clicking/extracting profile: {e}")
        
        return profile
    
    def _extract_side_panel_info(self) -> Dict[str, Any]:
        """
        Extract detailed profile information from the side panel.
        
        Returns:
            Dictionary with detailed profile fields
        """
        details = {
            "display_name": None,
            "username": None,
            "description": None,
            "location": None,
            "company": None,
            "about": None,
            "looking_for_teammates": False,
            "project_description": None,
            "i_am_a_roles": [],
            "looking_for_roles": [],
            "interested_in_topics": [],
            "avatar_url": None,
            "profile_url": None,
            "tags": [],
            "languages": [],
        }
        
        try:
            # Get the right sidebar panel content
            # The profile detail is shown in a persistent right sidebar
            panel_selectors = [
                'aside.xl\\:block',  # Right sidebar (escaped colon)
                'aside:has-text("VIEW")',  # Aside with VIEW PROFILE
                'aside:has-text("@")',  # Aside with username
                'div[class*="sticky"][class*="top"][class*="w-1/4"]',  # Sticky right column
                'div[class*="w-1/4"]:has-text("@")',  # Right column with username
                'aside',  # Any aside element
            ]
            
            panel = None
            for selector in panel_selectors:
                try:
                    el = self.page.query_selector(selector)
                    if el:
                        text = el.inner_text().strip()
                        # Make sure it has actual content
                        if text and len(text) > 50 and ('@' in text or 'VIEW' in text.upper() or 'LOOKING' in text.upper()):
                            panel = el
                            print(f"    Found panel with selector: {selector[:50]}")
                            break
                except Exception as e:
                    continue
            
            # If still not found, try all aside elements
            if not panel:
                try:
                    all_asides = self.page.query_selector_all('aside')
                    for aside in all_asides:
                        text = aside.inner_text().strip()
                        if text and len(text) > 50:
                            panel = aside
                            print(f"    Found aside element with content")
                            break
                except:
                    pass
            
            if not panel:
                print("    Right panel not found or empty")
                return details
            
            panel_text = panel.inner_text()
            panel_html = panel.inner_html()
            
            # Extract avatar URL from img tag
            try:
                avatar_img = panel.query_selector('img[src*="static.narrative"]')
                if avatar_img:
                    details['avatar_url'] = avatar_img.get_attribute('src')
            except:
                pass
            
            # Extract data from the right panel
            # The panel structure: VIEW PROFILE header, avatar, name, roles, location, languages, sections
            
            # Extract username (format: @username)
            username_matches = re.findall(r'@(\w+)', panel_text)
            if username_matches:
                # Take the first username found (should be the main one)
                details['username'] = f"@{username_matches[0]}"
            
            # Extract display name - look for text before username or after "VIEW PROFILE"
            # Try to find name that's not a section header
            lines = [l.strip() for l in panel_text.split('\n') if l.strip()]
            
            # Look for display name - usually appears early, before @username
            for i, line in enumerate(lines):
                if line.startswith('@'):
                    # Check previous line for display name
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        # Skip section headers
                        if prev_line and not prev_line.startswith(('//', 'VIEW', 'LOOKING', 'I AM', 'INTERESTED', 'ABOUT')) and len(prev_line) < 50:
                            details['display_name'] = prev_line
                            break
                    # Also check if username line has name before @
                    if ' ' in line:
                        parts = line.split('@')
                        if len(parts) > 0 and parts[0].strip():
                            details['display_name'] = parts[0].strip()
                    break
            
            # Extract tags (format: # TAG NAME)
            tag_matches = re.findall(r'#\s*([A-Z\s/]+)', panel_text)
            details['tags'] = [tag.strip() for tag in tag_matches if len(tag.strip()) > 1]
            
            # Extract location - look for city names or location patterns
            # Location often appears as text like "Toronto", "Nairobi", "Abuja, Nigeria"
            location_patterns = [
                r'📍\s*([^\n]+)',
                r'Location[:\s]+([^\n]+)',
                # Look for common city patterns (capitalized words, possibly with comma)
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+)?)\b(?=\s*(?:English|Spanish|Japanese|Russian|Yoruba|French|German|Chinese|$))',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, panel_text)
                if match:
                    loc = match.group(1).strip()
                    # Filter out common false positives
                    if loc and len(loc) > 2 and loc.lower() not in ['view', 'looking', 'about', 'interested']:
                        details['location'] = loc
                        break
            
            # Extract company/organization - look for patterns like "Co-Founder @ Kormos", "founder", etc.
            company_patterns = [
                r'Co-Founder\s+@\s*([A-Z][a-zA-Z\s]+)',  # Co-Founder @ Company
                r'Founder\s+@\s*([A-Z][a-zA-Z\s]+)',  # Founder @ Company
                r'founder\s+&?\s*engr\s+@\s*([a-zA-Z]+)',  # founder & engr @ company
                r'@\s*([A-Z][a-zA-Z\s]{2,30})(?=\s|$)',  # @ Company (standalone)
                r'(?:Working at|at)\s+([A-Z][a-zA-Z\s]+)',  # Working at Company
            ]
            for pattern in company_patterns:
                match = re.search(pattern, panel_text, re.IGNORECASE)
                if match:
                    company = match.group(1).strip()
                    if company and len(company) < 50:
                        details['company'] = company
                        break
            
            # Extract languages
            language_keywords = ['English', 'Spanish', 'Japanese', 'Russian', 'Yoruba', 'French', 'German', 'Chinese']
            details['languages'] = [lang for lang in language_keywords if lang in panel_text]
            
            # Extract "Looking for teammates" section
            if 'looking for teammates' in panel_text.lower() or 'looking for teammate' in panel_text.lower():
                details['looking_for_teammates'] = True
                
                # Extract project description
                project_match = re.search(r'looking for teammates[^\n]*\n([^\n]+(?:\n[^\n]+){0,2})', panel_text, re.IGNORECASE)
                if project_match:
                    details['project_description'] = project_match.group(1).strip()
            
            # Extract sections - look for "//" headers which indicate sections
            # Sections like: "// VIEW PROFILE", "// LOOKING FOR", "// I AM A", etc.
            
            # Find all section markers
            section_markers = {
                'i_am_a': [r'//\s*I\s+AM\s+A', r'I\s+AM\s+A', r'//\s*I\'M\s+A'],
                'looking_for': [r'//\s*LOOKING\s+FOR', r'LOOKING\s+FOR'],
                'interested_in': [r'//\s*INTERESTED\s+IN', r'INTERESTED\s+IN'],
                'about': [r'//\s*ABOUT', r'ABOUT'],
                'looking_for_teammates': [r'//\s*LOOKING\s+FOR\s+TEAMMATES', r'LOOKING\s+FOR\s+TEAMMATES'],
            }
            
            # Extract "I AM A" roles
            for pattern in section_markers['i_am_a']:
                i_am_a_match = re.search(f'{pattern}[^\n]*\n((?:[^\n]+\n?)+?)(?=\n(?://|LOOKING|INTERESTED|ABOUT|$))', panel_text, re.IGNORECASE | re.DOTALL)
                if i_am_a_match:
                    section_text = i_am_a_match.group(1)
                    # Extract role tags (they might be in # format or just text)
                    roles = re.findall(r'#\s*([A-Z\s/]+)', section_text)
                    if not roles:
                        # Try to extract role-like text (all caps, short phrases)
                        roles = re.findall(r'\b([A-Z][A-Z\s/]{2,30})\b', section_text)
                    details['i_am_a_roles'] = [r.strip() for r in roles if r.strip() and len(r.strip()) < 50]
                    break
            
            # Extract "LOOKING FOR" roles
            for pattern in section_markers['looking_for']:
                looking_for_match = re.search(f'{pattern}[^\n]*\n((?:[^\n]+\n?)+?)(?=\n(?://|I\s+AM|INTERESTED|ABOUT|$))', panel_text, re.IGNORECASE | re.DOTALL)
                if looking_for_match:
                    section_text = looking_for_match.group(1)
                    roles = re.findall(r'#\s*([A-Z\s/]+)', section_text)
                    if not roles:
                        roles = re.findall(r'\b([A-Z][A-Z\s/]{2,30})\b', section_text)
                    details['looking_for_roles'] = [r.strip() for r in roles if r.strip() and len(r.strip()) < 50]
                    break
            
            # Extract "INTERESTED IN" topics
            for pattern in section_markers['interested_in']:
                interested_match = re.search(f'{pattern}[^\n]*\n((?:[^\n]+\n?)+?)(?=\n(?://|I\s+AM|LOOKING|ABOUT|$))', panel_text, re.IGNORECASE | re.DOTALL)
                if interested_match:
                    section_text = interested_match.group(1)
                    topics = re.findall(r'#\s*([A-Z\s/]+)', section_text)
                    if not topics:
                        topics = re.findall(r'\b([A-Z][A-Z\s/]{2,30})\b', section_text)
                    details['interested_in_topics'] = [t.strip() for t in topics if t.strip() and len(t.strip()) < 50]
                    break
            
            # Extract "ABOUT" section
            for pattern in section_markers['about']:
                about_match = re.search(f'{pattern}[^\n]*\n((?:[^\n]+\n?)+?)(?=\n(?://|I\s+AM|LOOKING|INTERESTED|$))', panel_text, re.IGNORECASE | re.DOTALL)
                if about_match:
                    details['about'] = about_match.group(1).strip()
                    break
            
            # Extract "LOOKING FOR TEAMMATES" section
            for pattern in section_markers['looking_for_teammates']:
                teammates_match = re.search(f'{pattern}[^\n]*\n((?:[^\n]+\n?)+?)(?=\n(?://|I\s+AM|LOOKING|INTERESTED|ABOUT|$))', panel_text, re.IGNORECASE | re.DOTALL)
                if teammates_match:
                    details['looking_for_teammates'] = True
                    details['project_description'] = teammates_match.group(1).strip()
                    break
            
            # Extract description (short bio, usually near the top)
            if not details['description']:
                # Look for text that's not a tag, username, or section header
                desc_match = re.search(r'@\w+\s*\n([^\n#@•]{10,200})', panel_text)
                if desc_match:
                    candidate = desc_match.group(1).strip()
                    if not any(keyword in candidate.lower() for keyword in ['looking', 'interested', 'about', 'i am']):
                        details['description'] = candidate
            
            # Try to extract profile URL from View Profile button or link
            try:
                view_profile_link = panel.query_selector('a[href*="/profiles/"]')
                if view_profile_link:
                    details['profile_url'] = view_profile_link.get_attribute('href')
                    if details['profile_url'] and not details['profile_url'].startswith('http'):
                        details['profile_url'] = f"{self.base_url}{details['profile_url']}"
            except:
                pass
            
            # Extract from MESSAGE button context - indicates company/work
            # Look for work/company info
            work_indicators = ['founder', 'co-founder', 'ceo', 'cto', 'engineer at', 
                             'working at', 'building', '@']
            for line in lines:
                line_lower = line.lower()
                for indicator in work_indicators:
                    if indicator in line_lower and '@' not in line:
                        if not details['company'] and len(line) < 100:
                            details['company'] = line
                            break
            
            # Extract location
            location_patterns = [
                r'📍\s*(.+)',
                r'Location:\s*(.+)',
            ]
            for line in lines:
                for pattern in location_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        details['location'] = match.group(1).strip()
                        break
            
            # Extract languages
            language_keywords = ['english', 'spanish', 'chinese', 'japanese', 'russian', 
                               'portuguese', 'french', 'german', 'korean', 'hindi',
                               'arabic', 'indonesian', 'italian', 'turkish', 'vietnamese',
                               'yoruba', 'afrikaans']
            for line in lines:
                line_lower = line.lower()
                for lang in language_keywords:
                    if lang in line_lower:
                        # This line contains language info
                        langs = [l.strip() for l in line.split(',')]
                        details['languages'] = [l for l in langs if any(lk in l.lower() for lk in language_keywords)]
                        break
            
        except Exception as e:
            print(f"    Error extracting side panel info: {e}")
            import traceback
            traceback.print_exc()
        
        return details
    
    def get_profile_cards(self) -> List[Dict[str, Any]]:
        """
        Extract profile cards - first from API interception, then from DOM.
        
        Returns:
            List of profile card data dictionaries
        """
        # If we have API data, use that (it's more reliable)
        if self.api_profiles:
            print(f"Using {len(self.api_profiles)} profiles from API interception")
            return self._normalize_api_profiles(self.api_profiles)
        
        # Fall back to DOM scraping
        print("No API data, falling back to DOM scraping...")
        return self._scrape_profiles_from_dom()
    
    def _normalize_api_profiles(self, api_profiles: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize API profile data to our standard format."""
        normalized = []
        
        for i, profile in enumerate(api_profiles):
            try:
                # Handle different API response formats
                normalized_profile = {
                    "card_index": i,
                    "username": None,
                    "display_name": None,
                    "description": None,
                    "location": None,
                    "tags": [],
                    "languages": [],
                    "company": None,
                    "looking_for_teammates": False,
                    "project_description": None,
                    "i_am_a_roles": [],
                    "looking_for_roles": [],
                    "interested_in_topics": [],
                    "about": None,
                    "profile_url": None,
                    "avatar_url": None,
                }
                
                # Map common field names
                field_mappings = {
                    'username': ['username', 'handle', 'user_name', 'userName'],
                    'display_name': ['display_name', 'displayName', 'name', 'full_name', 'fullName'],
                    'description': ['description', 'bio', 'short_bio', 'shortBio'],
                    'location': ['location', 'city', 'country'],
                    'company': ['company', 'organization', 'org'],
                    'about': ['about', 'bio', 'description', 'longBio'],
                    'avatar_url': ['avatar_url', 'avatarUrl', 'avatar', 'image', 'profileImage'],
                }
                
                for our_field, api_fields in field_mappings.items():
                    for api_field in api_fields:
                        if api_field in profile and profile[api_field]:
                            normalized_profile[our_field] = profile[api_field]
                            break
                
                # Handle username format
                if normalized_profile['username'] and not normalized_profile['username'].startswith('@'):
                    normalized_profile['username'] = f"@{normalized_profile['username']}"
                
                # Handle arrays
                array_mappings = {
                    'tags': ['tags', 'roles', 'skills'],
                    'languages': ['languages', 'language'],
                    'i_am_a_roles': ['i_am_a_roles', 'iAmARoles', 'myRoles'],
                    'looking_for_roles': ['looking_for_roles', 'lookingForRoles', 'seekingRoles'],
                    'interested_in_topics': ['interested_in_topics', 'interestedInTopics', 'interests', 'topics'],
                }
                
                for our_field, api_fields in array_mappings.items():
                    for api_field in api_fields:
                        if api_field in profile:
                            value = profile[api_field]
                            if isinstance(value, list):
                                normalized_profile[our_field] = value
                            elif isinstance(value, str):
                                normalized_profile[our_field] = [value]
                            break
                
                # Handle boolean fields
                if 'looking_for_teammates' in profile:
                    normalized_profile['looking_for_teammates'] = bool(profile['looking_for_teammates'])
                elif 'lookingForTeammates' in profile:
                    normalized_profile['looking_for_teammates'] = bool(profile['lookingForTeammates'])
                
                # Build profile URL
                if normalized_profile['username']:
                    clean_username = normalized_profile['username'].lstrip('@')
                    normalized_profile['profile_url'] = f"{self.base_url}/profiles/{clean_username}"
                
                # Only add if we have a username
                if normalized_profile['username']:
                    normalized.append(normalized_profile)
                    
            except Exception as e:
                print(f"Error normalizing profile {i}: {e}")
                continue
        
        return normalized
    
    def _scrape_profiles_from_dom(self) -> List[Dict[str, Any]]:
        """Scrape profiles directly from the DOM as fallback."""
        profile_cards = []
        
        try:
            # Wait a bit more for content
            time.sleep(3)
            
            # Try scrolling to trigger lazy loading
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            # Get page content for debugging
            page_html = self.page.content()
            
            # Save for debugging
            try:
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(page_html)
                print("Saved page HTML to debug_page.html")
            except:
                pass
            
            # Try to find profile elements using JavaScript
            profiles_js = self.page.evaluate('''
                () => {
                    const profiles = [];
                    
                    // Look for profile card buttons
                    const buttons = document.querySelectorAll('button.border-gray-dark-6');
                    
                    buttons.forEach((btn, index) => {
                        const text = btn.innerText || '';
                        const usernameMatch = text.match(/@(\\w+)/);
                        
                        if (usernameMatch) {
                            profiles.push({
                                card_index: index,
                                username: '@' + usernameMatch[1],
                                text_content: text.substring(0, 500),
                            });
                        }
                    });
                    
                    return profiles;
                }
            ''')
            
            print(f"JS extraction found {len(profiles_js)} profiles")
            
            for card in profiles_js:
                profile = {
                    'card_index': card.get('card_index', 0),
                    'username': card.get('username'),
                    'display_name': None,
                    'description': None,
                    'location': None,
                    'tags': [],
                    'languages': [],
                }
                
                # Parse text content to extract more info
                text_content = card.get('text_content', '')
                lines = [l.strip() for l in text_content.split('\n') if l.strip()]
                
                # Find display name (line before @username)
                for i, line in enumerate(lines):
                    if line.startswith('@') and i > 0:
                        profile['display_name'] = lines[i-1]
                        break
                
                profile_cards.append(profile)
            
            return profile_cards
            
        except Exception as e:
            print(f"Error in DOM scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _clean_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove internal fields that shouldn't be saved to database."""
        cleaned = data.copy()
        cleaned.pop('card_index', None)
        cleaned.pop('element', None)  # Remove element reference
        return cleaned
    
    def scrape_all_profiles(self, existing_usernames: set = None, max_profiles: int = None) -> List[Dict[str, Any]]:
        """
        Scrape all profiles from the profiles page, clicking each to get details.
        
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
        
        # Get profile card elements for clicking
        card_elements = self.get_profile_card_elements()
        
        if not card_elements:
            print("\n[ERROR] No profile cards found!")
            print("Possible causes:")
            print("  1. Cookies have expired - please refresh your cookies")
            print("  2. The site structure has changed")
            print("  3. Page didn't load properly")
            
            # Fall back to API data if available
            if self.api_profiles:
                print("\nFalling back to API data...")
                profile_data = self._normalize_api_profiles(self.api_profiles)
                for data in profile_data:
                    if data.get('username') not in existing_usernames:
                        profiles.append(self._clean_profile_data(data))
                return profiles
            
            return profiles
        
        # Limit to max_profiles if specified
        if max_profiles and len(card_elements) > max_profiles:
            card_elements = card_elements[:max_profiles]
            print(f"\nLimited to {max_profiles} profiles")
        
        print(f"\n[OK] Found {len(card_elements)} profiles to process")
        
        # First pass: extract basic info to check which to skip
        basic_info = []
        for i, card in enumerate(card_elements):
            info = self.extract_basic_info_from_card(card)
            info['card_index'] = i
            info['element'] = card
            basic_info.append(info)
        
        skip_count = len([c for c in basic_info if c.get('username') in existing_usernames])
        print(f"Skipping {skip_count} existing profiles\n")
        
        # Process each profile - click and extract details
        for i, card_info in enumerate(basic_info, 1):
            username = card_info.get("username")
            card_element = card_info.get("element")
            
            if not username:
                continue
                
            if username in existing_usernames:
                print(f"[{i}/{len(basic_info)}] Skipping existing: {username}")
                continue
            
            print(f"[{i}/{len(basic_info)}] Processing: {username}")
            
            try:
                # Click profile and extract detailed info
                complete_profile = self.click_profile_and_extract_details(card_element, i-1)
                
                # Ensure username is set
                if not complete_profile.get('username'):
                    complete_profile['username'] = username
                
                # Clean the data and add metadata
                complete_profile = self._clean_profile_data(complete_profile)
                complete_profile["source_url"] = self.profiles_url
                
                # Build profile URL if not set
                if not complete_profile.get('profile_url') and username:
                    clean_username = username.lstrip('@')
                    complete_profile['profile_url'] = f"{self.base_url}/profiles/{clean_username}"
                
                profiles.append(complete_profile)
                print(f"    [OK] Added {username}")
                
                # Small delay between profiles
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(f"    [ERROR] Error processing {username}: {e}")
                continue
        
        return profiles
    
    def save_debug_info(self, filename: str = "debug_info.json"):
        """Save debug information for troubleshooting."""
        debug_data = {
            "api_responses": self.api_responses,
            "api_profiles_count": len(self.api_profiles),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, default=str)
            print(f"Saved debug info to {filename}")
        except Exception as e:
            print(f"Error saving debug info: {e}")