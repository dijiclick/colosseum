import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Turkish month names (URL parameters)
MONTHS = [
    "ocak", "subat", "mart", "nisan", "mayis", "haziran",
    "temmuz", "agustos", "eylul", "ekim", "kasim", "aralik"
]

# Crawl range configuration
START_YEAR = 2025
START_MONTH = "aralik"
END_YEAR = 2026
END_MONTH = "kasim"

# Base URL
BASE_URL = "https://www.kongreuzmani.com"

# Request settings - be respectful to the server
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# Concurrency settings
MAX_WORKERS = 5

# Database table name
TABLE_NAME = "kongre_events"
