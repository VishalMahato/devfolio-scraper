# Devfolio Builders API Documentation

This document explains the behavior and structure of the Devfolio Search API used to fetch builder profiles.

## Endpoint
`POST https://api.devfolio.co/api/search/builders`

## Headers
The API requires standard browser-like headers. Without `origin`, `referer`, and a valid `user-agent`, the requests may be blocked or return 403 Forbidden.

```json
{
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://devfolio.co",
    "referer": "https://devfolio.co/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

## Request Payload
The backend uses Elasticsearch. The payload controls the search queries, pagination, and sorting.

```json
{
    "most": "projects_built",
    "locations": ["Kolkata"],
    "from": 0,
    "size": 50
}
```

### Supported Parameters
*   **`most`** (Sort by): 
    *   `"projects_built"` (default)
    *   `"hackathons_attended"`
    *   `"hackathons_won"`
*   **`locations`**: Array of string locations to filter by (e.g. `["Mumbai", "Bangalore"]`). Leave empty `[]` to search globally.
*   **`from`**: The starting offset for pagination (0-based).
*   **`size`**: Number of results per page (max tested: around 50-100).

## Response Structure
The response is returned in a typical Elasticsearch format, wrapping the actual profile inside `hits.hits[]._source`.

```json
{
  "hits": {
    "total": {
      "value": 10000,
      "relation": "gte"
    },
    "hits": [
      {
        "_source": {
          "uuid": "xxxxx-xxxx-xxxx-xxxx-xxxxx",
          "username": "johndoe",
          "first_name": "John",
          "last_name": "Doe",
          "profile_image": "https://...",
          "total_hackathons_attended": 5,
          "total_hackathons_won": 1,
          "total_projects": 3,
          "total_merits": 10,
          "total_funding_received": 0,
          "ama_enabled": false
        }
      }
    ]
  }
}
```

## Restrictions & The 10,000 Limit
Elasticsearch has a hard cap restriction where you cannot paginate past `from + size = 10000`. 
If you try to request `from: 10000`, the API will return a 400 Error.

**Workaround implemented/suggested**:
To scrape more than 10,000 total builders, you must break down the requests by adding strict filters (e.g. iterating through a list of Indian cities in the `locations` array) or changing the `most` sorting field to run multiple passes of 10,000.
