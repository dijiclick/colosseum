# All API Fields Captured

This document lists ALL fields that are now captured from the Colosseum API.

## Database Schema Fields

### Basic Profile Information
- `user_id` (INTEGER) - userId from API (unique identifier)
- `username` (TEXT) - Username with @ prefix (e.g., "@zsh28")
- `display_name` (TEXT) - Display name
- `description` (TEXT) - Short description (if available)
- `location` (TEXT) - City and country (e.g., "Nairobi, Kenya")
- `avatar_url` (TEXT) - Avatar image URL

### Education & Employment
- `is_university_student` (BOOLEAN) - Whether user is a student
- `current_position` (TEXT) - Current job position/role
- `company` (TEXT) - Company/organization name (extracted from currentPosition)

### Arrays (JSONB)
- `tags` (JSONB) - Skills array from API (e.g., ["Anchor", "Rust", "Typescript"])
- `languages` (JSONB) - Languages spoken (e.g., ["English", "Spanish"])
- `i_am_a_roles` (JSONB) - jobRoles from API (e.g., ["Software Engineer", "Backend Developer"])
- `looking_for_roles` (JSONB) - rolesLookingFor from API
- `interested_in_topics` (JSONB) - interestedUseCases from API (e.g., ["DeFi"])
- `account_roles` (JSONB) - accountRoles from profile object
- `batches` (JSONB) - batches from profile object

### Collaboration
- `looking_for_teammates` (BOOLEAN) - lookingForCollab from API
- `project_description` (TEXT) - lookingToBuild from API

### Additional Info
- `about` (TEXT) - Full bio/about text
- `profile_url` (TEXT) - URL to profile page (e.g., "https://arena.colosseum.org/profiles/zsh28")

### Social Media Handles
- `github_handle` (TEXT) - GitHub username (e.g., "zsh28")
- `linkedin_handle` (TEXT) - LinkedIn URL or handle
- `twitter_handle` (TEXT) - Twitter/X username (e.g., "zeeshdev28")
- `telegram_handle` (TEXT) - Telegram handle (can be null)

### Metadata
- `source_url` (TEXT) - Original URL where profile was found
- `scraped_at` (TIMESTAMP) - When profile was scraped
- `created_at` (TIMESTAMP) - When record was created
- `updated_at` (TIMESTAMP) - When record was last updated

## API Field Mapping

### From List Endpoint (`/api/users/profiles`)
| API Field | Database Field | Notes |
|-----------|---------------|-------|
| `userId` | `user_id` | Unique identifier |
| `username` | `username` | With @ prefix added |
| `displayName` | `display_name` | |
| `city` | `location` | Combined with country |
| `country` | `location` | Combined with city |
| `avatarUrl` | `avatar_url` | |
| `yourRoles` | `i_am_a_roles` | |
| `isUniversityStudent` | `is_university_student` | |
| `currentPosition` | `current_position` | |
| `languages` | `languages` | |

### From Detailed Endpoint (`/api/v2/users/profile`)

#### From `profile` object:
| API Field | Database Field | Notes |
|-----------|---------------|-------|
| `id` | `user_id` | If not set from list |
| `displayName` | `display_name` | If not set from list |
| `username` | `username` | If not set from list |
| `avatarUrl` | `avatar_url` | If not set from list |
| `accountRoles` | `account_roles` | JSONB array |
| `batches` | `batches` | JSONB array |

#### From `extendedProfile` object:
| API Field | Database Field | Notes |
|-----------|---------------|-------|
| `country` | `location` | Combined with city |
| `city` | `location` | Combined with country |
| `languages` | `languages` | JSONB array |
| `about` | `about` | Full bio text |
| `isUniversityStudent` | `is_university_student` | Boolean |
| `githubHandle` | `github_handle` | |
| `linkedinHandle` | `linkedin_handle` | |
| `twitterHandle` | `twitter_handle` | |
| `telegramHandle` | `telegram_handle` | |
| `lookingForCollab` | `looking_for_teammates` | Boolean |
| `lookingToBuild` | `project_description` | |
| `currentPosition` | `current_position` | Also parsed for company |
| `jobRoles` | `i_am_a_roles` | JSONB array |
| `rolesLookingFor` | `looking_for_roles` | JSONB array |
| `skills` | `tags` | JSONB array |
| `interestedUseCases` | `interested_in_topics` | JSONB array |

## Example Complete Profile Data

```json
{
  "user_id": 28741,
  "username": "@zsh28",
  "display_name": "zsh28",
  "location": "Nairobi, Kenya",
  "avatar_url": "https://static.narrative-violation.com/...",
  "is_university_student": false,
  "current_position": "Software Developer",
  "company": "Software Developer",
  "looking_for_teammates": true,
  "project_description": "",
  "tags": ["Anchor", "APIs / Backend Web", "UIs / Frontend Web", "React Native", "Rust", "Smart Contracts", "Typescript", "LLMs / Neural Networks"],
  "languages": ["English"],
  "i_am_a_roles": ["Software Engineer", "Backend Developer", "Frontend Developer"],
  "looking_for_roles": ["Backend Developer", "Frontend Developer", "Software Engineer"],
  "interested_in_topics": ["DeFi"],
  "about": "Full-stack dev specializing in Rust, Node.js & Solana with ~1 year pro experience, shipped projects & OSS work. First-Class Honours BSc Computer Science, Cardiff University.",
  "profile_url": "https://arena.colosseum.org/profiles/zsh28",
  "github_handle": "zsh28",
  "linkedin_handle": "https://www.linkedin.com/in/zeeshanali-gulamhusein/",
  "twitter_handle": "zeeshdev28",
  "telegram_handle": null,
  "account_roles": [],
  "batches": []
}
```

## Next Steps

1. **Run the updated SQL script** (`setup_colosseum_database.sql`) in Supabase to add all new columns
2. **Re-run the scraper** - it will now capture ALL fields from the API
3. **Verify data** - Check that all fields are being populated correctly

