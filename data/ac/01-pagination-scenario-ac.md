Story ID: STORY-0001
Feature: Product List Pagination
Actor/Role: API Consumer
Goal/Benefit: Allow API consumers to retrieve products using cursor-based pagination so they can fetch pages efficiently and predictably.
Out of scope:
- Filtering and sorting behavior for product lists
- Creation, update, or deletion of products

AC-1: Retrieve first page with default limit
Given the GET /products endpoint is available
And 50 products exist in the catalog
When the client requests GET /products with no query parameters
Then the HTTP response status is 200
And the response body "data" array contains 20 items
And the response body "pagination.limit" is 20
And the response body "pagination.count" is 20
And the response body "pagination.has_next" is true
And the response body "pagination.has_previous" is false
And the response body "pagination.next_cursor" is not null
And the response body "pagination.previous_cursor" is null
And the response body "pagination.total_count" is 50

AC-2: Configurable page size (examples)
Given the GET /products endpoint is available
And 120 products exist in the catalog
When the client requests GET /products?limit=<Limit>
Then the HTTP response status is 200
And the response body "pagination.limit" is <Limit>
And the response body "pagination.count" is <ExpectedCount>

Examples:
| Case | Limit | ExpectedCount |
|------|-------|---------------|
| 1    | 1     | 1             |
| 2    | 20    | 20            |
| 3    | 100   | 100           |

AC-3: Limit exceeding maximum returns error
Given the GET /products endpoint is available
And 200 products exist in the catalog
When the client requests GET /products?limit=150
Then the HTTP response status is 400
And the response body is exactly {"error":"limit must be between 1 and 100"}

AC-4: Invalid cursor returns error
Given the GET /products endpoint is available
And 100 products exist in the catalog
And the client provides a cursor value "invalid_cursor_token" that is not recognized by the system
When the client requests GET /products?cursor=invalid_cursor_token
Then the HTTP response status is 400
And the response body is exactly {"error":"Invalid cursor"}

AC-5: Requesting last page indicates no next page
Given the GET /products endpoint is available
And 50 products exist in the catalog
And the client has a valid cursor "cursor_page3" that refers to the third page with limit 20
When the client requests GET /products?cursor=cursor_page3&limit=20
Then the HTTP response status is 200
And the response body "data" array contains 10 items
And the response body "pagination.count" is 10
And the response body "pagination.has_next" is false
And the response body "pagination.next_cursor" is null
And the response body "pagination.has_previous" is true
And the response body "pagination.previous_cursor" is not null

AC-6: Performance under load
Given a pre-agreed performance test harness and representative query parameters
When 100 concurrent clients request GET /products?limit=20 for a sustained 1 minute test
Then p95 latency for successful requests is ≤ 300 ms (measured by the pre-agreed test harness)
And the error rate is ≤ 1%, where "error" is defined as any response with an HTTP status other than 200
And the test results include: total requests, number of successful responses (200), number of errored responses (≠200), p50, p95, p99 latencies, and throughput (requests/sec) for verification.