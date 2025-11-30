# Colosseum Profiles Crawler

A Python web crawler that extracts user profile data from [arena.colosseum.org/profiles](https://arena.colosseum.org/profiles) and stores it in Supabase.

## Features

- 🔐 Authenticated crawling using browser cookies
- 🤖 Playwright-based browser automation
- 📊 Stores data in Supabase PostgreSQL database
- 🔄 Automatic duplicate detection (skip existing profiles)
- 📝 Extracts comprehensive profile information including:
  - Basic info: username, display name, tags, description, location, languages
  - Detailed info: company, looking for teammates, project description, roles, topics, about section

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Set Up Supabase Database

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Run the contents of `setup_colosseum_database.sql`

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 4. Configure Cookies

1. Export your browser cookies from arena.colosseum.org
2. Save the cookies JSON file (default path: `c:\Users\ariad\OneDrive\Desktop\colosium cookie.txt`)
3. Or update the path in `colosseum_main.py` with `--cookies` argument

### 5. Run the Crawler

```bash
# Crawl 100 profiles
python colosseum_main.py --limit 100

# Dry run - see what would be scraped
python colosseum_main.py --dry-run

# Run in visible browser mode
python colosseum_main.py --visible

# Force re-scrape existing profiles
python colosseum_main.py --no-skip-existing

# Test database connection
python colosseum_main.py --test-db
```

## Configuration

Edit `config.py` to change:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- Cookie file path can be specified via `--cookies` argument

## Data Extracted

For each profile:

| Field | Description |
|-------|-------------|
| username | Username (e.g., "@dopevelli") |
| display_name | Display name |
| description | Short description |
| location | Location (e.g., "Toronto") |
| tags | Array of role tags (JSONB) |
| languages | Array of languages (JSONB) |
| company | Company/organization |
| looking_for_teammates | Boolean flag |
| project_description | Project description from "Looking for teammates" |
| i_am_a_roles | Array of user's roles (JSONB) |
| looking_for_roles | Array of roles user is looking for (JSONB) |
| interested_in_topics | Array of topics of interest (JSONB) |
| about | Full about text |
| profile_url | URL to profile page |
| avatar_url | Avatar image URL |
| source_url | Original URL where profile was found |

## File Structure

```
colosseum-crawler/
├── .env                      # Supabase credentials (not in git)
├── .gitignore                # Git ignore rules
├── requirements.txt               # Python dependencies
├── config.py                 # Configuration
├── colosseum_cookie_handler.py  # Cookie loading
├── colosseum_scraper.py      # Playwright scraping logic
├── colosseum_database.py     # Supabase operations
├── colosseum_main.py         # Entry point
├── setup_colosseum_database.sql  # SQL for table creation
└── README.md                 # This file
```

## Troubleshooting

### "401 Unauthorized" errors
- Your cookies have expired
- Re-export cookies from browser after logging in
- Make sure cookies are for both `arena.colosseum.org` and `api.colosseum.org`

### "Table does not exist" error
- Run `setup_colosseum_database.sql` in Supabase SQL Editor

### Profiles not loading
- The page uses JavaScript to load profiles dynamically
- Wait time may need to be increased in `colosseum_scraper.py`
- Check browser console for errors

### Playwright not found
- Run `playwright install chromium` after installing requirements

### Clicking profiles not working
- Profile detail extraction requires clicking on profile cards
- This feature is being improved
- Basic profile data is still extracted from listing cards

## License

For personal use only. Respect Colosseum's terms of service.
