"""
Main entry point for Colosseum Profiles Crawler
"""

import argparse
import sys
from datetime import datetime
from colosseum_scraper import ColosseumScraper
from colosseum_database import ColosseumDatabase


def main():
    """Main entry point for the Colosseum crawler."""
    parser = argparse.ArgumentParser(
        description='Crawl Colosseum.org profiles and store in Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python colosseum_main.py                           # Full crawl
  python colosseum_main.py --reverse                 # Start from last user ID and work backwards
  python colosseum_main.py --dry-run                 # See what would be scraped
  python colosseum_main.py --headless                # Run in headless mode
  python colosseum_main.py --no-skip-existing       # Re-scrape existing profiles
  python colosseum_main.py --test-db                 # Test database connection
        """
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Print profiles without actually scraping'
    )
    parser.add_argument(
        '--no-skip-existing', 
        action='store_true',
        help='Force re-scrape profiles that already exist in database'
    )
    parser.add_argument(
        '--headless', 
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    parser.add_argument(
        '--visible', 
        action='store_true',
        help='Run browser in visible mode (overrides headless)'
    )
    parser.add_argument(
        '--cookies', 
        type=str, 
        default=r"C:\Users\Administrator\Desktop\colosseum crawler\colosium cookie.txt",
        help='Path to cookies JSON file'
    )
    parser.add_argument(
        '--test-db', 
        action='store_true',
        help='Test database connection and exit'
    )
    parser.add_argument(
        '--limit', 
        type=int,
        help='Maximum number of profiles to scrape (default: all)'
    )
    parser.add_argument(
        '--reverse', 
        action='store_true',
        help='Start from the last user ID and work backwards to the first'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 60)
    print("  Colosseum.org Profiles Crawler")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize database
    try:
        db = ColosseumDatabase()
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        print("Please check your .env file and Supabase credentials.")
        return 1
    
    # Test connection mode
    if args.test_db:
        if db.test_connection():
            count = db.get_profile_count()
            print(f"Total profiles in database: {count}")
            return 0
        else:
            return 1
    
    # Initialize scraper
    try:
        # If --visible is set, run in visible mode, otherwise headless
        headless_mode = not args.visible
        scraper = ColosseumScraper(cookies_file=args.cookies, headless=headless_mode)
        scraper.start()
    except Exception as e:
        print(f"Failed to initialize scraper: {e}")
        print("Please check that Playwright is installed: pip install playwright && playwright install chromium")
        return 1
    
    try:
        # Get existing usernames to skip
        existing_usernames = set()
        if not args.no_skip_existing:
            print("Fetching existing profiles from database...")
            existing_usernames = db.get_existing_usernames()
            print(f"Found {len(existing_usernames)} existing profiles")
            print()
        
        # Scrape profiles
        if args.dry_run:
            print("DRY RUN MODE - No data will be saved")
            print()
            # Just navigate and show what would be scraped
            if scraper.navigate_to_profiles():
                cards = scraper.get_profile_cards()
                print(f"\nWould scrape {len(cards)} profiles:")
                for card in cards[:10]:  # Show first 10
                    username = card.get("username", "Unknown")
                    display_name = card.get("display_name", "")
                    print(f"  - {username} ({display_name})")
                if len(cards) > 10:
                    print(f"  ... and {len(cards) - 10} more")
        else:
            # Actual scraping with immediate save
            max_profiles = args.limit if hasattr(args, 'limit') and args.limit else None
            
            # Track statistics
            total_inserted = 0
            total_updated = 0
            
            # Define save callback for immediate saving
            def save_profile_immediately(profile):
                nonlocal total_inserted, total_updated
                username = profile.get("username", "Unknown")
                
                # Check if it exists to determine insert vs update
                if username in existing_usernames:
                    total_updated += 1
                else:
                    total_inserted += 1
                
                return db.insert_profile(profile)
            
            # Scrape with immediate save callback
            profiles = scraper.scrape_all_profiles(
                existing_usernames, 
                max_profiles=max_profiles,
                save_callback=save_profile_immediately,
                reverse=args.reverse
            )
            
            if not profiles:
                print("\nNo new profiles found to scrape.")
                return 0
            
            # Print summary
            print(f"\n{'=' * 60}")
            print("  SCRAPING COMPLETE")
            print(f"{'=' * 60}")
            print(f"Total profiles scraped: {len(profiles)}")
            print(f"New profiles inserted: {total_inserted}")
            print(f"Existing profiles updated: {total_updated}")
            print(f"Total profiles in database: {db.get_profile_count()}")
            print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    except KeyboardInterrupt:
        print("\n\nCrawling interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError during crawling: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Always close browser
        scraper.stop()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

