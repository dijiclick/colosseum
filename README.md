# KongreUzmani.com Web Crawler

A Python web crawler that extracts Turkish medical/scientific congress event data from kongreuzmani.com and stores it in Supabase.

## Features

- 🔐 Authenticated crawling using browser cookies
- 📊 Stores data in Supabase PostgreSQL database
- 🔄 Automatic duplicate detection (skip existing events)
- 📅 Configurable date range crawling
- ⏱️ Polite crawling with rate limiting
- 📝 Extracts: Title, Date, Venue, Website, Description

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase Database

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Run the contents of `setup_database.sql`

### 3. Configure Cookies

1. Install a browser extension like "EditThisCookie" or "Cookie-Editor"
2. Log in to kongreuzmani.com with your subscription
3. Export all cookies as JSON
4. Save as `cookies.json` in the project folder

### 4. Run the Crawler

```bash
# Full crawl (Nov 2025 to Nov 2026)
python main.py

# Dry run - see what would be scraped
python main.py --dry-run

# Specific month only
python main.py --year 2025 --month aralik

# Force re-scrape existing
python main.py --no-skip-existing

# Test database connection
python main.py --test-db
```

## Configuration

Edit `config.py` to change:

- `START_YEAR`, `START_MONTH`: Beginning of crawl range
- `END_YEAR`, `END_MONTH`: End of crawl range
- `REQUEST_DELAY`: Seconds between requests (default: 2)
- `MAX_RETRIES`: Number of retry attempts
- `TIMEOUT`: Request timeout in seconds

## Data Extracted

For each congress event:

| Field | Description |
|-------|-------------|
| title | Event name |
| kongre_tarihi | Date (e.g., "16 Aralık - 20 Aralık 2025") |
| kongre_yeri | Venue/Location |
| kongre_web_sitesi | Official website URL |
| davet | Description/invitation text |
| source_url | Original URL |
| year | Event year |
| month | Event month (Turkish) |

## File Structure

```
kongreuzmani-crawler/
├── .env                 # Supabase credentials
├── cookies.json         # Browser cookies (you create this)
├── requirements.txt     # Python dependencies
├── config.py           # Configuration
├── cookie_handler.py   # Cookie loading
├── scraper.py          # Web scraping logic
├── database.py         # Supabase operations
├── main.py             # Entry point
├── setup_database.sql  # SQL for table creation
└── README.md           # This file
```

## Troubleshooting

### "401/403 Unauthorized" errors
- Your cookies have expired
- Re-export cookies from browser after logging in

### "Table does not exist" error
- Run `setup_database.sql` in Supabase SQL Editor

### Data not being extracted
- Website HTML structure may have changed
- Check the actual HTML and update selectors in `scraper.py`

### Rate limiting
- Increase `REQUEST_DELAY` in `config.py`
- Add random delays between requests

## Turkish Month Reference

| Turkish | English |
|---------|---------|
| ocak | January |
| subat | February |
| mart | March |
| nisan | April |
| mayis | May |
| haziran | June |
| temmuz | July |
| agustos | August |
| eylul | September |
| ekim | October |
| kasim | November |
| aralik | December |

## License

For personal use only. Respect kongreuzmani.com's terms of service.
