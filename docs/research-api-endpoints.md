# Research API Endpoints

This document describes the research-specific API endpoints available to users with researcher permissions.

## Authentication

All research endpoints support two authentication methods:

### Option 1: API Key (Recommended for Scripts)

Use an API key for programmatic access via the `X-API-Key` header:

```bash
curl -X GET "https://social-rv.com/api/research/sessions" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Option 2: Session Cookie (Browser-based)

For browser-based access, you can use your session cookie:

1. Open your browser's developer tools (F12 or right-click → Inspect)
2. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Under **Cookies**, find your domain
4. Copy the entire cookie value for the session cookie
5. Include it in your requests using the `Cookie` header

---

## Sessions Endpoints

### GET `/api/research/sessions`

Retrieves session data with enhanced information for researchers, including signed URLs for target data and session media.

#### Access Requirements

- Valid API key OR user with `is_researcher = true` in their user record

#### Query Parameters

##### Pagination (List Mode)

| Parameter                    | Type    | Default     | Description                                                                  |
| ---------------------------- | ------- | ----------- | ---------------------------------------------------------------------------- |
| `display_name`               | string  | -           | Filter sessions by user display name (case-insensitive)                      |
| `include_unsubmitted`        | boolean | false       | Include unsubmitted sessions                                                 |
| `include_non_public`         | boolean | true        | Include non-public sessions (researchers default to seeing private sessions) |
| `include_low_value_sessions` | boolean | false       | Include sessions marked as low-value                                         |
| `page`                       | integer | 1           | Page number for pagination                                                   |
| `page_size`                  | integer | 25          | Number of sessions per page                                                  |
| `sort_key`                   | string  | "SUBMITTED" | Sort column (see available keys below)                                       |
| `sort_direction`             | string  | "desc"      | Sort direction ("asc" or "desc")                                             |

##### Single ID Lookup

| Parameter | Type   | Description                          |
| --------- | ------ | ------------------------------------ |
| `id`      | string | Get a single session by its UUID     |

##### Bulk ID Lookup

| Parameter | Type   | Description                                           |
| --------- | ------ | ----------------------------------------------------- |
| `ids`     | string | Comma-separated list of session UUIDs (max 100)       |

#### Available Sort Keys

- `USER` - User display name
- `SUBMITTED` - Submission time
- `STARTED` - Tasking time
- `DURATION` - Session duration
- `COORDINATE` - Target coordinate
- `SESSION_TYPE` - Session type (weekly vs practice)
- `SELF_SCORE` - User's self-assessment score
- `COMMUNITY_SCORE` - Community rating average
- `P_VALUE` - Statistical p-value
- `RANK` - AI scoring rank
- `Z_SCORE` - Statistical z-score
- `TEXT_SIMILARITY` - Vector text similarity
- `CJ_RANK` - Comparative judging rank
- `COMMENTS` - Number of comments
- `PUBLIC` - Public/private status
- `LOW_VALUE` - Low-value flag
- `BLOCKCHAIN_VERIFIED` - Blockchain verification status

#### Response Format (List Mode)

```json
{
  "sessions": [
    {
      "id": "session_uuid",
      "is_low_value": false,
      "is_public": true,
      "tasking_time": "2024-01-01T12:00:00Z",
      "submission_time": "2024-01-01T13:30:00Z",
      "target_coordinate": "A1B2C3",
      "weekly_target_id": null,
      "self_score": 7,
      "p_value": 0.025,
      "rank": 15,
      "rank_denominator": 100,
      "vectorTextSimilarity": 0.75,
      "z_score": 1.96,
      "comparative_judging_rank": 8,
      "num_comments": 3,
      "community_score": {
        "average": 6.5,
        "num_scores": 4
      },
      "user": {
        "user_id": "user_uuid",
        "display_name": "RemoteViewer123"
      },
      "is_blockchain_verified": false,
      "targetData": {
        "description": "A red brick building with white trim",
        "imageUrl": "https://supabase.co/storage/v1/object/sign/target_media/path/to/image.jpg?token=...",
        "targetId": "target_uuid"
      },
      "sessionMediaUrls": [
        {
          "url": "https://supabase.co/storage/v1/object/sign/rv_session_files/path/to/session1.pdf?token=...",
          "mime_type": "application/pdf",
          "storage_path": "user_uuid/session_uuid/session1.pdf"
        }
      ],
      "decoyIds": ["decoy1_uuid", "decoy2_uuid", "decoy3_uuid"]
    }
  ],
  "total_count": 150,
  "page": 1,
  "page_size": 25,
  "total_pages": 6
}
```

#### Response Format (Single ID)

```json
{
  "session": {
    "id": "session_uuid",
    // ... same fields as list mode
  }
}
```

#### Response Format (Bulk IDs)

```json
{
  "sessions": [...],
  "total_count": 5,
  "requested_ids": ["id1", "id2", "id3", "id4", "id5"],
  "found_ids": ["id1", "id2", "id4"],
  "missing_ids": ["id3", "id5"]
}
```

#### Enhanced Fields for Researchers

- **`targetData`**: Object containing target information (only for submitted sessions)
  - `description`: Text description of the target
  - `imageUrl`: Signed URL to download the target image (expires in 1 hour)
  - `targetId`: UUID of the target

- **`sessionMediaUrls`**: Array of session media files (only for submitted sessions)
  - `url`: Signed URL to download the file (expires in 1 hour)
  - `mime_type`: File MIME type (e.g., "application/pdf", "image/jpeg")
  - `storage_path`: Internal storage path for reference

- **`decoyIds`**: Array of target UUIDs used as decoys in comparative judging

---

## Targets Endpoints

### GET `/api/research/targets`

Retrieves target data with signed URLs for target images.

#### Access Requirements

- Valid API key OR user with `is_researcher = true` in their user record

#### Query Parameters

##### Pagination (List Mode)

| Parameter        | Type    | Default      | Description                                     |
| ---------------- | ------- | ------------ | ----------------------------------------------- |
| `page`           | integer | 1            | Page number for pagination                      |
| `page_size`      | integer | 25           | Number of targets per page (max 100)            |
| `pool_name`      | string  | -            | Filter by pool name (case-insensitive)          |
| `target_pool_id` | string  | -            | Filter by target pool UUID                      |
| `sort_key`       | string  | "created_at" | Sort column                                     |
| `sort_direction` | string  | "desc"       | Sort direction ("asc" or "desc")                |

##### Single ID Lookup

| Parameter | Type   | Description                        |
| --------- | ------ | ---------------------------------- |
| `id`      | string | Get a single target by its UUID    |

##### Bulk ID Lookup

| Parameter | Type   | Description                                         |
| --------- | ------ | --------------------------------------------------- |
| `ids`     | string | Comma-separated list of target UUIDs (max 100)      |

#### Available Sort Keys

- `created_at` - Creation timestamp
- `coordinate` - Target coordinate
- `description` - Target description
- `pool_name` - Pool name

#### Response Format (List Mode)

```json
{
  "targets": [
    {
      "id": "target_uuid",
      "coordinate": "A1B2C3",
      "description": "A red brick building with white trim",
      "pool_name": "Default Pool",
      "target_pool_id": "pool_uuid",
      "created_at": "2024-01-01T12:00:00Z",
      "imageUrl": "https://supabase.co/storage/v1/object/sign/target_media/path/to/image.jpg?token=...",
      "ai_caption": "A two-story red brick building with white window frames and a black roof"
    }
  ],
  "total_count": 500,
  "page": 1,
  "page_size": 25,
  "total_pages": 20
}
```

#### Response Format (Single ID)

```json
{
  "target": {
    "id": "target_uuid",
    // ... same fields as list mode
  }
}
```

#### Response Format (Bulk IDs)

```json
{
  "targets": [...],
  "total_count": 5,
  "requested_ids": ["id1", "id2", "id3", "id4", "id5"],
  "found_ids": ["id1", "id2", "id4"],
  "missing_ids": ["id3", "id5"]
}
```

---

## Usage Examples

### Basic Request with API Key

```bash
curl -X GET "https://social-rv.com/api/research/sessions" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Get a Single Session by ID

```bash
curl -X GET "https://social-rv.com/api/research/sessions?id=abc123-def456" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Bulk Get Multiple Sessions

```bash
curl -X GET "https://social-rv.com/api/research/sessions?ids=id1,id2,id3,id4,id5" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Get a Single Target by ID

```bash
curl -X GET "https://social-rv.com/api/research/targets?id=target-uuid-here" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Bulk Get Multiple Targets

```bash
curl -X GET "https://social-rv.com/api/research/targets?ids=t1,t2,t3" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Include Low-Value Sessions

```bash
curl -X GET "https://social-rv.com/api/research/sessions?include_low_value_sessions=true" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Filter by User

```bash
curl -X GET "https://social-rv.com/api/research/sessions?display_name=RemoteViewer123" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Custom Pagination and Sorting

```bash
curl -X GET "https://social-rv.com/api/research/sessions?page=2&page_size=50&sort_key=P_VALUE&sort_direction=asc" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Python Example

```python
import requests

# Your API key
api_key = "YOUR_API_KEY"

# Base URL
base_url = "https://social-rv.com"

headers = {
    "X-API-Key": api_key
}

# Fetch sessions with pagination
def fetch_all_sessions():
    all_sessions = []
    page = 1
    
    while True:
        params = {
            "page": page,
            "page_size": 100,
            "include_low_value_sessions": "true"
        }
        
        response = requests.get(
            f"{base_url}/api/research/sessions",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        
        all_sessions.extend(data["sessions"])
        
        if page >= data["total_pages"]:
            break
        page += 1
    
    return all_sessions

# Fetch specific sessions by ID
def fetch_sessions_by_ids(session_ids):
    params = {
        "ids": ",".join(session_ids)
    }
    
    response = requests.get(
        f"{base_url}/api/research/sessions",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()

# Fetch a single target by ID
def fetch_target(target_id):
    params = {"id": target_id}
    
    response = requests.get(
        f"{base_url}/api/research/targets",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()["target"]

# Example usage
sessions = fetch_all_sessions()
print(f"Found {len(sessions)} sessions")

# Get target details for a session
for session in sessions[:5]:
    if session.get("targetData") and session["targetData"].get("targetId"):
        target = fetch_target(session["targetData"]["targetId"])
        print(f"Session {session['id']}: Target {target['description'][:50]}...")
```

---

## Error Responses

### 400 Bad Request

Invalid parameters provided (e.g., empty IDs list, too many IDs).

### 401 Unauthorized

User is not logged in, session has expired, or invalid API key.

### 404 Not Found

Requested session or target ID does not exist.

### 500 Internal Server Error

Server error occurred while processing the request.

---

## Notes

- **Signed URLs expire after 1 hour** - You'll need to refresh to get new URLs
- **Rate limiting** may apply to prevent abuse
- **Maximum 100 IDs** per bulk request to prevent timeout issues
- **File downloads** should be done promptly after fetching the data
- **Target data and media URLs** are only available for submitted sessions
- **Unsubmitted sessions** will have `null` values for `targetData` and empty arrays for `sessionMediaUrls`
- **Decoy IDs** can be used with the targets bulk endpoint to fetch all decoys for comparative judging analysis
