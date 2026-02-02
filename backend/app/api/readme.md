# Job Posting API Integration Documentation

## Overview

This directory contains integration scripts for multiple job posting APIs used to ingest job data for the Job Hunting AI Web Tool. All APIs are configured to search for U.S.-based jobs and/or remote, with a focus on computer science and software engineering positions. SUBJECT TO CHANGE***
---

## APIs Used

### 1. Adzuna
- **Type**: Job aggregator API
- **Base URL**: `https://api.adzuna.com/v1/api/jobs/us/search/{page}`
- **Authentication**: Required (API Key + App ID)
- **Coverage**: Aggregates postings from many ATS platforms and employer sites
- **Geographic Focus**: United States
- **Data Returned**: Job title, company, location, salary, description, source URL, publication date
- **Notes**: Broad geographic coverage with normalized responses. Supports pagination via page number in URL path.

### 2. Arbeitnow
- **Type**: Job aggregator API
- **Base URL**: `https://www.arbeitnow.com/api/job-board-api`
- **Authentication**: None
- **Coverage**: European companies and remote roles
- **Geographic Focus**: Global (filtered for remote/US positions)
- **Data Returned**: Job title, company, location, tags, remote flag, description, salary range, publication date
- **Notes**: Stable JSON schema with simple pagination. Supports remote job filtering.

### 3. Remotive
- **Type**: Job aggregator API
- **Base URL**: `https://remotive.com/api/remote-jobs`
- **Authentication**: None
- **Coverage**: Remote jobs aggregated from multiple ATS job boards
- **Geographic Focus**: Remote positions (global)
- **Data Returned**: Job metadata, categories, descriptions, publication date, salary information, company details
- **Notes**: Remote-focused dataset with consistent structure. Returns all active jobs in a single call.

### 4. RemoteOK
- **Type**: Job aggregator API
- **Base URL**: `https://remoteok.com/api`
- **Authentication**: None
- **Coverage**: Tech-focused roles sourced from many ATS systems
- **Geographic Focus**: US, LIKE US, or Remote positions
- **Data Returned**: Job title, company, tags, description, timestamps, salary information, location
- **Notes**: Lightweight JSON feed suitable for frequent polling. Tech-focused dataset.

### 5. USAJobs
- **Type**: Government job aggregator API
- **Base URL**: `https://data.usajobs.gov/api/Search`
- **Authentication**: Required (API Key in Authorization-Key header)
- **Coverage**: United States federal government roles
- **Geographic Focus**: United States
- **Data Returned**: Structured job postings, locations, pay grades, schedules, security clearance requirements, telework eligibility
- **Notes**: Highly structured and authoritative source for federal government positions.

### 6. The Muse
- **Type**: Job aggregator API
- **Base URL**: `https://www.themuse.com/api/public/v2/jobs`
- **Authentication**: Required (API Key in X-Muse-Api-Key header)
- **Coverage**: Tech and professional job postings from various companies
- **Geographic Focus**: United States (with location filtering support)
- **Data Returned**: Job title, company, location, categories, levels, description, publication date, salary information
- **Notes**: Well-structured API with support for category, level, location, and company filtering. Good for tech and professional roles.

### 7. SerpAPI (Google Jobs)
- **Type**: Job search aggregation API (Google Jobs results)
- **Base URL**: `https://serpapi.com/search.json`
- **Engine**: `google_jobs`
- **Authentication**: Required (API Key)
- **Coverage**: Google Jobs listings aggregated from company career pages, ATS platforms, and job boards
- **Geographic Focus**: United States (via query parameters)
- **Data Returned**: Job title, company name, location, description or snippet, apply links, salary signals, posting date, job highlights
- **Notes**: Pagination handled via `next_page_token`. Google Jobs typically returns around 10 results per page regardless of requested count. Best used as a high relevance enrichment source rather than bulk ingestion.

### 8. Jobicy
- **Type**: Job aggregator API
- **Base URL**: `https://jobicy.com/api/v2/remote-jobs`
- **Authentication**: None
- **Coverage**: Remote jobs aggregated from multiple sources
- **Geographic Focus**: Remote positions (global, with geographic filtering support)
- **Data Returned**: Job title, company name, location, job industry, job type, job level, description, salary range, publication date, application URL
- **Notes**: All jobs are remote by default. Supports filtering by tag (job title/description), industry, geographic region, and count. Requires browser-like headers to bypass Cloudflare protection.

---

## Jobs We're Looking For

### Primary Search Criteria
- **Job Titles**: TBD
- **Location**: 
  - United States
  - US-based or US timezone positions

### Top 25 Computer Science Job Titles (2026)
The system also searches for the following high-demand computer science positions.

The top 25 job titles include:
- AI Engineer
- Machine Learning Engineer
- Cybersecurity Analyst
- Software Engineer
- Data Scientist
- Cloud Architect
- Data Engineer
- DevOps Engineer
- AI Consultant
- Technical Product Manager
- Full-Stack Developer
- AI/ML Researcher
- Data Architect
- Security Engineer
- Network Engineer
- Blockchain Developer
- Systems Analyst
- UX/UI Designer
- Datacenter Technician
- Quantitative Researcher
- Mobile App Developer
- Ethical Hacker
- Database Administrator
- SRE (Site Reliability Engineer)
- Solutions Architect

### Salary Range
- **Minimum**: $50,000
- **Maximum**: $150,000
- **Note**: Some APIs may not include salary information for all positions

---

## API Calls

### 1. Adzuna API

#### Endpoint
```
GET https://api.adzuna.com/v1/api/jobs/us/search/{page}
```

#### Authentication
- **Method**: Query parameters
- **Required Parameters**:
  - `app_id`: Adzuna Application ID
  - `app_key`: Adzuna API Key

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `app_id` | string | Yes | Adzuna Application ID |
| `app_key` | string | Yes | Adzuna API Key |
| `what` | string | Yes | Search keywords (job title) |
| `results_per_page` | integer | No | Number of results per page (default: 50) |
| `page` | integer | Yes | Page number (included in URL path) |

#### Example Request
```http
GET https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=YOUR_APP_ID&app_key=YOUR_API_KEY&what=Software%20Engineer&results_per_page=50
```

#### Response Structure
```json
{
  "results": [
    {
      "id": "string",
      "title": "string",
      "company": {
        "display_name": "string"
      },
      "location": {
        "display_name": "string"
      },
      "description": "string",
      "redirect_url": "string",
      "salary_min": number,
      "salary_max": number,
      "created": "string",
      "tags": ["string"]
    }
  ]
}
```

---

### 2. Arbeitnow API

#### Endpoint
```
GET https://www.arbeitnow.com/api/job-board-api
```

#### Authentication
- **Method**: None required

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number for pagination |

#### Example Request
```http
GET https://www.arbeitnow.com/api/job-board-api?page=1
```

#### Response Structure
```json
{
  "data": [
    {
      "id": "string",
      "title": "string",
      "company_name": "string",
      "location": "string",
      "remote": boolean,
      "tags": ["string"],
      "description": "string",
      "url": "string",
      "salary_min": number,
      "salary_max": number,
      "published_at": "string"
    }
  ]
}
```

#### Post-Processing Filters
- Remote jobs only (if `remote_only=True`)
- Keyword filtering (e.g., "Software Engineer")
- Salary range filtering ($50k-$150k)

---

### 3. Remotive API

#### Endpoint
```
GET https://remotive.com/api/remote-jobs
```

#### Authentication
- **Method**: None required

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Job category filter (e.g., "software-dev") |
| `search` | string | No | Search term to filter jobs |
| `limit` | integer | No | Limit number of results |

#### Example Request
```http
GET https://remotive.com/api/remote-jobs?category=software-dev&search=Software%20Engineer
```

#### Response Structure
```json
{
  "jobs": [
    {
      "id": number,
      "title": "string",
      "company_name": "string",
      "candidate_required_location": "string",
      "tags": ["string"],
      "description": "string",
      "url": "string",
      "salary": "string",
      "salary_min": number,
      "salary_max": number,
      "publication_date": "string"
    }
  ]
}
```

#### Notes
- Returns all currently active remote job listings in one response
- All jobs are remote by default
- Salary may be provided as a string (e.g., "$120k - $160k") requiring parsing

---

### 4. RemoteOK API

#### Endpoint
```
GET https://remoteok.com/api
```

#### Authentication
- **Method**: None required

#### Request Parameters
- **Note**: RemoteOK API does not support query parameters. All filtering is done client-side after receiving the full dataset.

#### Example Request
```http
GET https://remoteok.com/api
```

#### Response Structure
```json
[
  {
    "id": number,
    "date": "string",
    "company": "string",
    "position": "string",
    "location": "string",
    "tags": ["string"],
    "description": "string",
    "url": "string",
    "salary_min": number,
    "salary_max": number
  }
]
```

#### Post-Processing Filters
- **Location**: US, LIKE US, or Remote positions only
- **Keywords**: Filter by position title containing "Software Engineer"
- **Salary**: Only include jobs with salary information (if `require_salary=True`)
- **Salary Range**: Filter to $50k-$150k range

---

### 5. USAJobs API

#### Endpoint
```
GET https://data.usajobs.gov/api/Search
```

#### Authentication
- **Method**: HTTP Header
- **Header**: `Authorization-Key: YOUR_API_KEY`
- **Additional Headers**:
  - `Host: data.usajobs.gov`
  - `User-Agent: OSU Job Search Application`

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `Keyword` | string | Yes | Search keywords (e.g., "Software Engineer") |
| `Page` | integer | No | Page number for pagination |

#### Example Request
```http
GET https://data.usajobs.gov/api/Search?Keyword=Software%20Engineer&Page=1
Headers:
  Host: data.usajobs.gov
  User-Agent: OSU Job Search Application
  Authorization-Key: YOUR_API_KEY
```

#### Response Structure
```json
{
  "SearchResult": {
    "SearchResultItems": [
      {
        "MatchedObjectId": "string",
        "MatchedObjectDescriptor": {
          "PositionID": "string",
          "PositionTitle": "string",
          "OrganizationName": "string",
          "DepartmentName": "string",
          "PositionLocation": [
            {
              "LocationName": "string"
            }
          ],
          "PositionLocationDisplay": "string",
          "PositionRemuneration": [
            {
              "MinimumRange": number,
              "MaximumRange": number,
              "Description": "string"
            }
          ],
          "PositionFormattedDescription": [
            {
              "Content": "string"
            }
          ],
          "ApplyURI": ["string"],
          "PositionURI": "string",
          "PositionStartDate": "string",
          "PositionEndDate": "string",
          "ApplicationCloseDate": "string",
          "JobCategory": [
            {
              "Name": "string"
            }
          ],
          "UserArea": {
            "Details": {
              "JobSummary": "string",
              "MajorDuties": ["string"],
              "Education": "string",
              "Requirements": "string",
              "HowToApply": "string",
              "Benefits": "string",
              "SecurityClearance": "string",
              "TeleworkEligible": boolean,
              "RemoteIndicator": boolean
            }
          }
        }
      }
    ]
  }
}
```

---

### 6. The Muse API

#### Endpoint
```
GET https://www.themuse.com/api/public/v2/jobs
```

#### Authentication
- **Method**: HTTP Header
- **Header**: `X-Muse-Api-Key: YOUR_API_KEY`

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number for pagination (default: 1) |
| `locations` | string | No | Location filter (e.g., "San Francisco Bay Area") |
| `company` | string | No | Company filter (e.g., "Google") |
| `level` | string | No | Job level filter (e.g., "Internship", "Entry Level", "Mid Level", "Senior Level") |
| `category` | string | No | Job category (e.g., "Software Engineering") |
| `sort` | string | No | Sort order (e.g., "newest", "oldest", "relevance") |

#### Example Request
```http
GET https://www.themuse.com/api/public/v2/jobs?page=1&category=Software%20Engineering&sort=newest
Headers:
  X-Muse-Api-Key: YOUR_API_KEY
```

#### Response Structure
```json
{
  "page": number,
  "page_count": number,
  "results": [
    {
      "id": number,
      "name": "string",
      "publication_date": "string",
      "company": {
        "name": "string"
      },
      "locations": [
        {
          "name": "string"
        }
      ],
      "categories": [
        {
          "name": "string"
        }
      ],
      "levels": [
        {
          "name": "string"
        }
      ],
      "contents": "string",
      "refs": {
        "landing_page": "string"
      },
      "salary_min": number,
      "salary_max": number
    }
  ]
}
```

#### Post-Processing Filters
- **Keywords**: Filter by job title containing "Software Engineer" (client-side)
- **Category**: Default to "Software Engineering" if not specified

---
### 7. SerpAPI (Google Jobs)

- **Type**: Job search aggregation API (Google Jobs results)
- **Base URL**: `https://serpapi.com/search.json`
- **Engine**: `google_jobs`
- **Authentication**: Required (API Key)
- **Coverage**: Google Jobs listings aggregated from company career pages, ATS platforms, and job boards
- **Geographic Focus**: United States (via query parameters)
- **Data Returned**: Job title, company name, location, description or snippet, apply links, salary signals, posting date, job highlights
- **Notes**: Pagination handled via `next_page_token`. Google Jobs typically returns around 10 results per page regardless of requested count.

#### Endpoint
GET https://serpapi.com/search.json?engine=google_jobs

#### Authentication
- Method: Query parameter
- Parameter: `api_key`

#### Required Python Dependency
pip install google-search-results

#### Request Parameters
| Parameter | Type | Required | Description |
|---------|------|----------|-------------|
| engine | string | Yes | Must be `google_jobs` |
| q | string | Yes | Job title or keywords, for example Software Engineer |
| location | string | No | Location filter, for example United States |
| google_domain | string | No | Defaults to google.com |
| hl | string | No | Language, default en |
| gl | string | No | Country code, default us |
| num | integer | No | Requested results per page, API typically caps at around 10 |
| next_page_token | string | No | Token used for pagination |
| api_key | string | Yes | SerpAPI API key |

#### Example Request
GET https://serpapi.com/search.json?engine=google_jobs&q=Software%20Engineer&location=United%20States&api_key=YOUR_API_KEY

#### Pagination
- Offset based pagination is not supported
- Pagination relies on `next_page_token` returned by the API
- Multiple requests are required to collect larger result sets such as 100 jobs

#### Response Structure (Simplified)
{
  "jobs_results": [
    {
      "title": "string",
      "company_name": "string",
      "location": "string",
      "description": "string",
      "apply_options": [
        { "link": "string" }
      ],
      "job_highlights": [],
      "posted_at": "string",
      "job_id": "string"
    }
  ],
  "pagination": {
    "next_page_token": "string"
  }
}

#### Post Processing and Normalization
SerpAPI job data is normalized into the standard ingestion schema:
- Company
- Position
- Location
- Tags
- Description
- URL
- Salary_Min
- Salary_Max
- Date
- ID



#### Usage Notes
- A valid SerpAPI key is required
- Subject to SerpAPI rate limits and Google Jobs availability
- Best used as a high relevance enrichment source rather than bulk ingestion
- Client side filtering is required for job titles, salary ranges, and locations

---

### 8. Jobicy API

#### Endpoint
```
GET https://jobicy.com/api/v2/remote-jobs
```

#### Authentication
- **Method**: None required
- **Note**: Requires browser-like headers to bypass Cloudflare protection

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tag` | string | No | Search by job title and description (default: "Software Engineer") |
| `industry` | string | No | Job category filter (e.g., "engineering", "marketing") |
| `geo` | string | No | Geographic filter (e.g., "usa", "canada", "emea") |
| `count` | integer | No | Number of listings to return (default: 100, range: 1-100) |

#### Required Headers
To bypass Cloudflare protection, include browser-like headers:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.9
Referer: https://jobicy.com/
Origin: https://jobicy.com
```

#### Example Request
```http
GET https://jobicy.com/api/v2/remote-jobs?tag=Software%20Engineer&geo=usa&count=100
Headers:
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  Accept: application/json, text/plain, */*
  Referer: https://jobicy.com/
```

#### Response Structure
```json
{
  "jobs": [
    {
      "id": "string",
      "jobTitle": "string",
      "companyName": "string",
      "jobGeo": "string",
      "jobIndustry": ["string"],
      "jobType": ["string"],
      "jobLevel": "string",
      "jobDescription": "string",
      "url": "string",
      "salaryMin": number,
      "salaryMax": number,
      "salaryCurrency": "string",
      "pubDate": "string"
    }
  ],
  "jobCount": number
}
```

#### Post-Processing Filters
- **Location**: All jobs are remote by default; geographic filtering via `geo` parameter
- **Keywords**: Filter by job title/description using `tag` parameter
- **Salary Range**: Filter to $50k-$150k range (client-side)
- **Industry**: Filter by job category using `industry` parameter

#### Notes
- All jobs returned are remote positions
- Maximum 100 results per request
- Supports geographic filtering (usa, canada, emea, etc.)
- Job industry, type, and level are provided as arrays
- HTML content in job descriptions requires cleaning during normalization

---

## Data Normalization

All APIs return data in different formats. The integration scripts normalize all job postings to a unified schema with the following fields:

### Standardized Fields
- **Company**: Company name
- **Position**: Job title
- **Location**: Job location (or "Remote")
- **Tags**: Semicolon-separated tags
- **Description**: Cleaned job description (HTML removed, whitespace normalized)
- **URL**: Application URL or job posting URL
- **Salary_Min**: Minimum salary (if available)
- **Salary_Max**: Maximum salary (if available)
- **Date**: Publication date
- **ID**: Unique job identifier from source API

### USAJobs Additional Fields
- **Department**: Department name
- **PositionID**: Government position ID
- **LocationDisplay**: Formatted location display
- **JobCategory**: Job category tags
- **MajorDuties**: Major duties description
- **Education**: Education requirements
- **Requirements**: Job requirements
- **HowToApply**: Application instructions
- **Benefits**: Benefits information
- **SecurityClearance**: Security clearance requirements
- **TeleworkEligible**: Telework eligibility (Yes/No)
- **RemoteIndicator**: Remote work indicator (Yes/No)
- **Salary_Rate**: Salary rate description
- **StartDate**: Position start date
- **EndDate**: Position end date
- **ApplicationCloseDate**: Application deadline

---

## Recommended Ingestion Order

1. **Adzuna** - Broad coverage, good normalization
2. **Arbeitnow** - European and remote positions
3. **Remotive** - Remote-focused dataset
4. **Jobicy** - Remote jobs with geographic filtering support
5. **SerpAPI** - Google Jobs search results for all tech-focused roles
6. **RemoteOK** - Tech-focused roles
7. **USAJobs** - Federal government positions
8. **The Muse** - Tech and professional roles with good filtering

---

## Rate Limits & Best Practices

### Rate Limits
- **Adzuna**: Check API documentation for rate limits
- **Arbeitnow**: No documented rate limits (use reasonable request frequency)
- **Remotive**: No documented rate limits (use reasonable request frequency)
- **Jobicy**: No documented rate limits (use reasonable request frequency, requires browser-like headers)
- **RemoteOK**: No documented rate limits (use reasonable request frequency)
- **USAJobs**: Check API documentation for rate limits
- **The Muse**: Check API documentation for rate limits
- **SerpAPI**: Check API documentation for rate limits

### Best Practices
1. Implement retry logic with exponential backoff for failed requests
2. Cache responses when appropriate to reduce API calls
3. Respect API terms of service and rate limits
4. Handle partial responses gracefully
5. Log API failures for monitoring and debugging
6. Use pagination to retrieve complete datasets
7. Filter results client-side when APIs don't support server-side filtering

---

## Error Handling

All integration scripts include error handling for:
- Network timeouts
- HTTP errors (4xx, 5xx)
- Invalid API responses
- Missing required fields
- Authentication failures

Errors are logged and scripts continue processing other jobs/APIs when possible.

---

## Output Format

All job data is exported to CSV files in the respective `csv/` subdirectories with timestamps:
- Format: `{api_name}_jobs_YYYYMMDD_HHMMSS.csv`
- Example: `adzuna_jobs_20260123_200337.csv`

---

## File Structure

```
api/
├── adzuna/
│   ├── test_adzuna_api.py
│   ├── test_adzuna_api_top25.py
│   └── csv/
├── arbeitnow/
│   ├── test_arbeitnow_api.py
│   └── csv/
├── remotive/
│   ├── test_remotive_api.py
│   ├── test_remotive_api_full.py
│   └── csv/
├── remoteok/
│   ├── test_remoteok_api.py
│   └── csv/
├── usajobs/
│   ├── test_usajobs_api.py
│   └── csv/
├── muse/
│   ├── test_muse_api.py
│   └── csv/
├── serpapi/
│   ├── test_serp_api.py
│   └── csv/
├── jobicy/
│   ├── test_jobicy_api.py
│   ├── job-icy logic.md
│   └── csv/
├── README.md (this file)
├── top-jobs.md
```

---

## Notes

- All APIs are configured for U.S.-focused job searches
- Remote positions are prioritized where available
- Salary information may not be available for all positions
- Some APIs require client-side filtering after receiving responses
- Data normalization ensures consistent schema across all sources
- CSV exports include all normalized fields for downstream processing
