"""
Web Scraper for Colosseum.org Profiles - API-Based Version
===========================================================
Uses direct API calls to fetch profile data efficiently.
"""

from playwright.sync_api import sync_playwright, Browser, BrowserContext, APIRequestContext
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

from colosseum_cookie_handler import load_colosseum_cookies, get_colosseum_headers


class ColosseumScraper:
    """Main scraper class using Playwright API requests"""
    
    def __init__(self, cookies_file: str = r"C:\Users\Administrator\Desktop\colosseum crawler\colosium cookie.txt", headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            cookies_file: Path to cookies JSON file
            headless: Whether to run browser in headless mode (not used, kept for compatibility)
        """
        self.cookies_file = cookies_file
        self.headless = headless
        self.base_url = "https://arena.colosseum.org"
        
        # Will be initialized in start()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.api_context: Optional[APIRequestContext] = None
        # Log file for API/debug information
        self.log_file = "colosseum_api_errors.log"
    
    def start(self):
        """Start the browser and API context."""
        self.playwright = sync_playwright().start()
        
        # Create browser (needed for API context)
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        # Create context (needed for cookies)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        # Load cookies and create API request context
        cookies = load_colosseum_cookies(self.cookies_file)
        cookie_header = self._build_cookie_header(cookies)
        headers = get_colosseum_headers()
        headers.update(cookie_header)
        
        self.api_context = self.playwright.request.new_context(
            base_url="https://api.colosseum.org",
            extra_http_headers=headers
        )
        
        print("Browser started successfully")
    
    def stop(self):
        """Stop the browser and API context."""
        if self.api_context:
            self.api_context.dispose()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("Browser stopped")

    def _log_api_error(self, source: str, url: str, status: int = None, error: str = "", response_text: str = "") -> None:
        """
        Append detailed API error information to a log file.

        Args:
            source: Which method logged this (e.g. 'fetch_profiles_list')
            url: Full request URL (path with query)
            status: HTTP status code (if available)
            error: Python exception message (if any)
            response_text: Optional response text/body (may be trimmed)
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            # Make sure we log in the current working directory
            log_path = os.path.join(os.getcwd(), self.log_file)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"[{timestamp}] SOURCE: {source}\n")
                f.write(f"URL: {url}\n")
                if status is not None:
                    f.write(f"STATUS: {status}\n")
                if error:
                    f.write(f"ERROR: {error}\n")
                if response_text:
                    # Avoid huge logs – limit to first 2000 characters
                    trimmed = response_text[:2000]
                    f.write("RESPONSE (truncated to 2000 chars):\n")
                    f.write(trimmed + "\n")
                f.write("\n")
        except Exception:
            # Do not crash the scraper if logging fails
            pass
    
    def _build_cookie_header(self, cookies: List[Dict[str, Any]]) -> Dict[str, str]:
        """Build Cookie header string from cookies list."""
        cookie_parts = []
        for cookie in cookies:
            if cookie.get("domain") == "api.colosseum.org" or "api.colosseum.org" in cookie.get("domain", ""):
                name = cookie.get("name")
                value = cookie.get("value")
                if name and value:
                    cookie_parts.append(f"{name}={value}")
        return {"Cookie": "; ".join(cookie_parts)} if cookie_parts else {}
    
    def fetch_profiles_list(self, limit: int = 12, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch profiles list from API endpoint.
        
        Args:
            limit: Number of profiles to fetch per page
            offset: Offset for pagination
            
        Returns:
            List of profile dictionaries
        """
        if not self.api_context:
            print("[ERROR] API context not initialized")
            return []
        
        try:
            # Generate queryStart timestamp (current time in milliseconds)
            query_start = int(time.time() * 1000)
            
            url = f"/api/users/profiles?queryStart={query_start}&limit={limit}&offset={offset}"
            
            print(f"  [API] Fetching profiles: limit={limit}, offset={offset}")
            
            response = self.api_context.get(url, timeout=30000)
            
            if response.status != 200:
                print(f"  [ERROR] API returned status {response.status}")
                # Log details for debugging (e.g. 401 at offset 1500)
                body_text = ""
                try:
                    body_text = response.text()
                except Exception as e:
                    body_text = f"<failed to read response body: {e}>"
                self._log_api_error(
                    source="fetch_profiles_list",
                    url=url,
                    status=response.status,
                    error="non-200 response",
                    response_text=body_text,
                )
                return []
            
            data = response.json()
            
            # Extract profiles from response
            profiles = []
            if isinstance(data, dict) and "profiles" in data:
                profiles = data["profiles"]
            elif isinstance(data, list):
                profiles = data
            
            print(f"  [OK] Fetched {len(profiles)} profiles from API")
            return profiles
            
        except Exception as e:
            print(f"  [ERROR] Failed to fetch profiles: {e}")
            import traceback
            traceback.print_exc()
            # Log exception
            self._log_api_error(
                source="fetch_profiles_list",
                url=f"/api/users/profiles?queryStart=<dynamic>&limit={limit}&offset={offset}",
                error=str(e),
            )
            return []
    
    def fetch_profile_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed profile information for a specific user.
        
        Args:
            user_id: The userId from the profile list
            
        Returns:
            Dictionary with profile and extendedProfile data, or None if failed
        """
        if not self.api_context:
            print(f"  [ERROR] API context not initialized for user {user_id}")
            return None
        
        try:
            url = f"/api/v2/users/profile?id={user_id}"
            
            response = self.api_context.get(url, timeout=30000)
            
            if response.status != 200:
                print(f"  [ERROR] API returned status {response.status} for user {user_id}")
                # Log details for debugging
                body_text = ""
                try:
                    body_text = response.text()
                except Exception as e:
                    body_text = f"<failed to read response body: {e}>"
                self._log_api_error(
                    source="fetch_profile_details",
                    url=url,
                    status=response.status,
                    error=f"non-200 response for user {user_id}",
                    response_text=body_text,
                )
                return None
            
            data = response.json()
            
            # The API returns both profile and extendedProfile
            return data
            
        except Exception as e:
            print(f"  [ERROR] Failed to fetch profile details for user {user_id}: {e}")
            # Log exception
            self._log_api_error(
                source="fetch_profile_details",
                url=f"/api/v2/users/profile?id={user_id}",
                error=str(e),
            )
            return None
    
    def _normalize_profile_data(self, list_profile: Dict[str, Any], detail_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Normalize profile data from API responses to match database schema.
        
        Args:
            list_profile: Profile data from /api/users/profiles
            detail_data: Optional detailed data from /api/v2/users/profile
            
        Returns:
            Normalized profile dictionary
        """
        profile = {
            # API identifiers
            "user_id": None,
            "username": None,
            "display_name": None,
            "description": None,
            "location": None,
            "tags": [],
            "languages": [],
            "company": None,
            "current_position": None,
            "is_university_student": False,
            "looking_for_teammates": False,
            "project_description": None,
            "i_am_a_roles": [],
            "looking_for_roles": [],
            "interested_in_topics": [],
            "about": None,
            "profile_url": None,
            "avatar_url": None,
            # Social media handles
            "github_handle": None,
            "linkedin_handle": None,
            "twitter_handle": None,
            "telegram_handle": None,
            # API metadata
            "account_roles": [],
            "batches": [],
        }
        
        # Extract from list profile
        if list_profile:
            # User ID
            profile["user_id"] = list_profile.get("userId") or list_profile.get("user_id")
            
            username = list_profile.get("username") or list_profile.get("userName")
            if username:
                profile["username"] = f"@{username}" if not username.startswith("@") else username
            
            profile["display_name"] = list_profile.get("displayName") or list_profile.get("display_name")
            city = list_profile.get("city")
            country = list_profile.get("country")
            
            # Build location from city and country
            location_parts = []
            if city:
                location_parts.append(city)
            if country:
                location_parts.append(country)
            profile["location"] = ", ".join(location_parts) if location_parts else None
            
            profile["avatar_url"] = list_profile.get("avatarUrl") or list_profile.get("avatar_url")
            
            # Extract roles from list profile
            your_roles = list_profile.get("yourRoles") or list_profile.get("your_roles") or []
            if isinstance(your_roles, list):
                profile["i_am_a_roles"] = your_roles
            elif isinstance(your_roles, str):
                profile["i_am_a_roles"] = [your_roles]
            
            # Extract languages
            languages = list_profile.get("languages") or []
            if isinstance(languages, list):
                profile["languages"] = languages
            elif isinstance(languages, str):
                profile["languages"] = [languages]
            
            # Extract other fields
            profile["is_university_student"] = bool(list_profile.get("isUniversityStudent") or list_profile.get("is_university_student"))
            profile["current_position"] = list_profile.get("currentPosition") or list_profile.get("current_position")
            
            # Build profile URL
            if profile["username"]:
                clean_username = profile["username"].lstrip("@")
                profile["profile_url"] = f"{self.base_url}/profiles/{clean_username}"
        
        # Extract from detailed profile if available
        if detail_data:
            extended = detail_data.get("extendedProfile") or {}
            profile_data = detail_data.get("profile") or {}
            
            # Update user_id if available
            if not profile.get("user_id"):
                profile["user_id"] = profile_data.get("id") or profile_data.get("userId")
            
            # Update basic info if missing
            if not profile.get("display_name"):
                profile["display_name"] = extended.get("displayName") or profile_data.get("displayName")
            
            if not profile.get("username"):
                username = extended.get("username") or profile_data.get("username")
                if username:
                    profile["username"] = f"@{username}" if not username.startswith("@") else username
            
            # Extended profile fields
            profile["about"] = extended.get("about")
            profile["current_position"] = extended.get("currentPosition") or profile.get("current_position")
            # Keep company separate - it might be extracted from currentPosition text
            if extended.get("currentPosition") and not profile.get("company"):
                # Try to extract company name from currentPosition if it contains @
                current_pos = extended.get("currentPosition", "")
                if "@" in current_pos:
                    parts = current_pos.split("@")
                    if len(parts) > 1:
                        profile["company"] = parts[-1].strip()
                else:
                    # If no @, use currentPosition as company
                    profile["company"] = current_pos
            
            # Roles
            job_roles = extended.get("jobRoles") or extended.get("job_roles") or []
            if isinstance(job_roles, list):
                profile["i_am_a_roles"] = job_roles if job_roles else profile.get("i_am_a_roles", [])
            elif isinstance(job_roles, str):
                profile["i_am_a_roles"] = [job_roles]
            
            profile["looking_for_roles"] = extended.get("rolesLookingFor") or extended.get("roles_looking_for") or []
            if isinstance(profile["looking_for_roles"], str):
                profile["looking_for_roles"] = [profile["looking_for_roles"]]
            
            # Topics/Use cases
            interested_topics = extended.get("interestedUseCases") or extended.get("interested_use_cases") or []
            if isinstance(interested_topics, list):
                profile["interested_in_topics"] = interested_topics
            elif isinstance(interested_topics, str):
                profile["interested_in_topics"] = [interested_topics]
            
            # Skills (add to tags)
            skills = extended.get("skills") or []
            if isinstance(skills, list):
                profile["tags"] = skills
            elif isinstance(skills, str):
                profile["tags"] = [skills]
            
            # Looking for teammates
            profile["looking_for_teammates"] = bool(extended.get("lookingForCollab") or extended.get("looking_for_collab"))
            profile["project_description"] = extended.get("lookingToBuild") or extended.get("looking_to_build")
            
            # University student status
            if extended.get("isUniversityStudent") is not None:
                profile["is_university_student"] = bool(extended.get("isUniversityStudent"))
            
            # Update languages if available
            lang = extended.get("languages") or []
            if lang:
                if isinstance(lang, list):
                    profile["languages"] = lang
                elif isinstance(lang, str):
                    profile["languages"] = [lang]
            
            # Update location if available
            if extended.get("city") or extended.get("country"):
                loc_parts = []
                if extended.get("city"):
                    loc_parts.append(extended["city"])
                if extended.get("country"):
                    loc_parts.append(extended["country"])
                if loc_parts:
                    profile["location"] = ", ".join(loc_parts)
            
            # Extract social media handles
            profile["github_handle"] = extended.get("githubHandle")
            profile["linkedin_handle"] = extended.get("linkedinHandle")
            profile["twitter_handle"] = extended.get("twitterHandle")
            profile["telegram_handle"] = extended.get("telegramHandle")
            
            # Extract profile metadata
            account_roles = profile_data.get("accountRoles") or profile_data.get("account_roles") or []
            if isinstance(account_roles, list):
                profile["account_roles"] = account_roles
            elif isinstance(account_roles, str):
                profile["account_roles"] = [account_roles]
            
            batches = profile_data.get("batches") or []
            if isinstance(batches, list):
                profile["batches"] = batches
            elif isinstance(batches, str):
                profile["batches"] = [batches]
        
        # Clean up None values in lists
        for key in ["tags", "languages", "i_am_a_roles", "looking_for_roles", "interested_in_topics", "account_roles", "batches"]:
            if profile.get(key) is None:
                profile[key] = []
            else:
                profile[key] = [item for item in profile[key] if item is not None and item != ""]
        
        return profile
    
    def _clean_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove internal fields that shouldn't be saved to database."""
        cleaned = data.copy()
        cleaned.pop('card_index', None)
        cleaned.pop('element', None)
        return cleaned
    
    def scrape_all_profiles(self, existing_usernames: set = None, max_profiles: int = None, save_callback=None) -> List[Dict[str, Any]]:
        """
        Scrape all profiles using the API directly.
        
        Args:
            existing_usernames: Set of usernames to skip
            max_profiles: Maximum number of profiles to scrape (None for all)
            save_callback: Optional callback function(profile_dict) to save immediately
            
        Returns:
            List of complete profile data dictionaries
        """
        if existing_usernames is None:
            existing_usernames = set()
        
        profiles = []
        saved_count = 0
        
        if not self.api_context:
            print("[ERROR] API context not initialized. Please call start() first.")
            return profiles
        
        print("\n[OK] Using API to fetch profiles directly (max speed)")
        
        # Fetch profiles with pagination - use max limit for faster fetching
        limit = 100  # Increased limit for faster fetching
        offset = 0
        total_fetched = 0
        
        while True:
            # Fetch a page of profiles
            list_profiles = self.fetch_profiles_list(limit=limit, offset=offset)
            
            if not list_profiles:
                print(f"\n[OK] No more profiles to fetch (fetched {total_fetched} total)")
                break
            
            print(f"\nProcessing {len(list_profiles)} profiles from API...")
            
            # Process each profile
            for list_profile in list_profiles:
                # Check if we've reached max_profiles
                if max_profiles and total_fetched >= max_profiles:
                    print(f"\n[OK] Reached max_profiles limit ({max_profiles})")
                    break
                
                user_id = list_profile.get("userId")
                username = list_profile.get("username") or list_profile.get("userName")
                
                if not username:
                    print(f"  [SKIP] Profile missing username (userId: {user_id})")
                    continue
                
                # Format username
                formatted_username = f"@{username}" if not username.startswith("@") else username
                
                # Skip if already exists
                if formatted_username in existing_usernames:
                    print(f"  [{total_fetched + 1}] Skipping existing: {formatted_username}")
                    total_fetched += 1
                    continue
                
                print(f"  [{total_fetched + 1}] Fetching details for: {formatted_username} (userId: {user_id})")
                
                # Fetch detailed profile information
                detail_data = None
                if user_id:
                    detail_data = self.fetch_profile_details(user_id)
                    # No delay - maximum speed
                
                # Normalize and combine data
                normalized_profile = self._normalize_profile_data(list_profile, detail_data)
                
                # Only process if we have a username
                if normalized_profile.get("username"):
                    cleaned_profile = self._clean_profile_data(normalized_profile)
                    profiles.append(cleaned_profile)
                    
                    # Save immediately if callback provided
                    if save_callback:
                        if save_callback(cleaned_profile):
                            saved_count += 1
                            print(f"    [OK] Saved to database: {formatted_username}")
                        else:
                            print(f"    [ERROR] Failed to save: {formatted_username}")
                    else:
                        print(f"    [OK] Extracted profile data for {formatted_username}")
                else:
                    print(f"    [ERROR] Failed to extract username for profile")
                
                total_fetched += 1
            
            # Check if we've reached max_profiles
            if max_profiles and total_fetched >= max_profiles:
                break
            
            # Check if we got fewer profiles than requested (last page)
            if len(list_profiles) < limit:
                print(f"\n[OK] Reached last page (got {len(list_profiles)} profiles, expected {limit})")
                break
            
            # Move to next page
            offset += limit
            # No delay - maximum speed
        
        print(f"\n[OK] Successfully scraped {len(profiles)} new profiles")
        if save_callback:
            print(f"[OK] Saved {saved_count} profiles to database immediately")
        return profiles

