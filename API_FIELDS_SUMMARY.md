# Colosseum API Fields Summary

## List Profiles Endpoint
**GET** `/api/users/profiles?queryStart={timestamp}&limit=12&offset=0`

### Response Structure:
```json
{
  "profiles": [...],
  "hasMore": true,
  "offset": 0
}
```

### Profile Fields (from list):
- `userId` (int) - Unique user ID
- `username` (string) - Username without @
- `avatarUrl` (string) - Avatar image URL
- `displayName` (string) - Display name
- `city` (string) - City name
- `yourRoles` (array) - Array of role strings (e.g., ["Software Engineer", "Frontend Developer"])
- `isUniversityStudent` (boolean) - Whether user is a student
- `currentPosition` (string) - Current job position/company
- `languages` (array) - Array of language strings (e.g., ["English", "Spanish"])

---

## Detailed Profile Endpoint
**GET** `/api/v2/users/profile?id={userId}`

### Response Structure:
```json
{
  "profile": {...},
  "extendedProfile": {...}
}
```

### `profile` Object Fields:
- `id` (int) - User ID
- `displayName` (string) - Display name
- `username` (string) - Username
- `avatarUrl` (string) - Avatar image URL
- `accountRoles` (array) - Account roles
- `batches` (array) - Batch information

### `extendedProfile` Object Fields:

#### Basic Info:
- `country` (string) - Country name
- `city` (string) - City name
- `languages` (array) - Languages spoken
- `about` (string) - Full bio/about text
- `isUniversityStudent` (boolean) - Student status
- `currentPosition` (string) - Current job/position

#### **SOCIAL MEDIA HANDLES** (What you need):
- `githubHandle` (string|null) - GitHub username (e.g., "zsh28")
- `linkedinHandle` (string|null) - LinkedIn URL or handle (e.g., "https://www.linkedin.com/in/zeeshanali-gulamhusein/")
- `twitterHandle` (string|null) - Twitter/X username (e.g., "zeeshdev28")
- `telegramHandle` (string|null) - Telegram handle (can be null)

#### Collaboration:
- `lookingForCollab` (boolean) - Looking for collaboration
- `lookingToBuild` (string) - Description of what they want to build

#### Roles & Skills:
- `jobRoles` (array) - Current job roles (e.g., ["Software Engineer", "Backend Developer"])
- `rolesLookingFor` (array) - Roles they're looking for
- `skills` (array) - Skills list (e.g., ["Anchor", "Rust", "Typescript"])
- `interestedUseCases` (array) - Use cases of interest (e.g., ["DeFi"])

---

## Example Full Response:

```json
{
  "profile": {
    "id": 28741,
    "displayName": "zsh28",
    "username": "zsh28",
    "avatarUrl": "https://static.narrative-violation.com/...",
    "accountRoles": [],
    "batches": []
  },
  "extendedProfile": {
    "country": "Kenya",
    "city": "Nairobi",
    "languages": ["English"],
    "about": "Full-stack dev specializing in Rust, Node.js & Solana...",
    "isUniversityStudent": false,
    "githubHandle": "zsh28",
    "linkedinHandle": "https://www.linkedin.com/in/zeeshanali-gulamhusein/",
    "twitterHandle": "zeeshdev28",
    "telegramHandle": null,
    "lookingForCollab": true,
    "lookingToBuild": "",
    "currentPosition": "Software Developer",
    "jobRoles": ["Software Engineer", "Backend Developer", "Frontend Developer"],
    "rolesLookingFor": ["Backend Developer", "Frontend Developer", "Software Engineer"],
    "skills": ["Anchor", "APIs / Backend Web", "UIs / Frontend Web", "React Native", "Rust", "Smart Contracts", "Typescript", "LLMs / Neural Networks"],
    "interestedUseCases": ["DeFi"]
  }
}
```

