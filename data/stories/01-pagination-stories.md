Feature: Product List Pagination
  As an API consumer, I want cursor-based pagination for GET /products so that I can retrieve product pages efficiently and predictably.

Background:
  Given the GET /products endpoint is available
  And the default limit is 20 and the maximum limit is 100

Scenario: Happy — retrieve first page with default limit
  Given 50 products exist in the catalog
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

Scenario: Happy — configurable page size (examples)
  Given 120 products exist in the catalog
  When the client requests GET /products?limit=<Limit>
  Then the HTTP response status is 200
  And the response body "pagination.limit" is <Limit>
  And the response body "pagination.count" is <ExpectedCount>
  Examples:
    | Case | Limit | ExpectedCount |
    | 1    | 1     | 1             |
    | 2    | 20    | 20            |
    | 3    | 100   | 100           |

Scenario: Negative — limit exceeding maximum returns error
  Given 200 products exist in the catalog
  When the client requests GET /products?limit=150
  Then the HTTP response status is 400
  And the response body is {"error":"limit must be between 1 and 100"}

Scenario: Negative — invalid cursor returns error
  Given 100 products exist in the catalog
  And the client provides a cursor value "invalid_cursor_token"
  When the client requests GET /products?cursor=invalid_cursor_token
  Then the HTTP response status is 400
  And the response body is {"error":"Invalid cursor"}

Scenario: Edge — requesting last page indicates no next page
  Given 50 products exist in the catalog
  And the client has a valid cursor "cursor_page3" that refers to the third page with limit 20
  When the client requests GET /products?cursor=cursor_page3&limit=20
  Then the HTTP response status is 200
  And the response body "data" array contains 10 items
  And the response body "pagination.count" is 10
  And the response body "pagination.has_next" is false
  And the response body "pagination.next_cursor" is null
  And the response body "pagination.has_previous" is true
  And the response body "pagination.previous_cursor" is not null

Scenario: Non-functional — performance under load
  When 100 concurrent clients request GET /products?limit=20 for a representative query over 1 minute
  Then p95 latency is ≤ 300 ms (measured in pre-agreed test)
  And the error rate is ≤ 1%