Story ID: STORY-0002
Feature: User table manual refresh
Actor/Role: Administrator
Goal/Benefit: Reload the latest Users table data without losing filters, sort, pagination, or scroll position.
Out of scope:
- Automatic/periodic background refresh behavior
- Changes to server-side pagination or filtering semantics

AC-1: Happy — Click Refresh updates data and preserves UI state
Given I am logged in as an administrator
And I have the Users table open with filter "active", sort "created_desc", page size 20
And the table currently displays rows for users with IDs 1001..1020
And the table is scrolled so row with user ID 1011 is visible in the viewport
And the system clock is 2025-10-24 15:00:00 UTC
When I click the "Refresh user data" button in the table toolbar
Then the refresh button shows a loading spinner
And the refresh button is disabled
And after the refresh completes the table rows update to include user ID 1050 in the current dataset
And the filter remains "active"
And the sort remains "created_desc"
And the table remains on the same pagination page
And the visible viewport still includes user ID 1011
And a toast appears with exact text "Data refreshed"
And the page displays "Last refreshed: 2025-10-24 15:00:00 UTC"

AC-2: Negative — Server error shows retryable error notification
Given I am on the Users table showing rows for user IDs 1001..1020
And the backend returns HTTP 500 for the refresh request
When I click the "Refresh user data" button
Then the refresh button shows a loading spinner
And a toast appears with exact text "Failed to refresh data"
And the toast displays a visible "Retry" action button
And the table continues to display the pre-refresh rows for users 1001..1020

AC-3: Edge — Keyboard activation (Enter / Space) triggers refresh
Given the "Refresh user data" button has keyboard focus
Examples:
| Key   |
| Enter |
| Space |
When I press the <Key> key
Then the refresh button shows a loading spinner
And the refresh button is disabled
And after the refresh completes a toast appears with exact text "Data refreshed"

AC-4: Edge — Duplicate activation prevented while request in progress
Given I have clicked the "Refresh user data" button and a refresh is in progress
When I click the "Refresh user data" button while the refresh is still in progress
Then the refresh button remains disabled
And no additional success toast appears while the original refresh is in progress
And only one "Data refreshed" toast appears when the original refresh finishes

AC-5: Negative — Request timeout handled with explicit timeout message
Given I am on the Users table showing rows for user IDs 1001..1020
And the refresh request exceeds 10 seconds without a response
When I click the "Refresh user data" button
Then the refresh button shows a loading spinner
And a toast appears with exact text "Failed to refresh data: request timed out"
And the toast displays a visible "Retry" action button
And the table continues to display the pre-refresh rows for users 1001..1020

AC-6: Non-functional — Refresh performance and reliability under load
When 1,000 refresh actions are executed over 5 minutes from 50 concurrent users in the pre-agreed test environment
Then p95 latency for refresh actions (measured end-to-end from client action to UI update completion) is ≤ 500 ms
And error rate across refresh actions is ≤ 1% (errors counted as HTTP 5xx, timeouts, or client-side failures)
And the test run uses the pre-agreed test environment and measurement tooling agreed with SRE/product before execution

AC-7: Observability — Actions and failures are auditable
Given a refresh action is performed (successful or failed)
When the action completes or fails
Then an entry is recorded in the system audit/log with: timestamp, initiating admin user ID, refresh outcome (success / HTTP status / timeout), and server response time
And the audit/log entry is queryable in the pre-agreed diagnostics tooling for verification within the test environment