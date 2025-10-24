Feature: User table manual refresh
As an administrator, I want a Refresh button for the Users table so that I can reload the latest user data without losing filters, sort, pagination, or scroll position.

Background:
  Given I am logged in as an administrator
  And I have the Users table open with filter "active", sort "created_desc", page size 20
  And the table currently displays rows for users with IDs 1001..1020

Scenario: Happy — Click Refresh updates data and preserves UI state
  Given the table is scrolled so row with user ID 1011 is visible in the viewport
  And the system clock is 2025-10-24 15:00:00 UTC
  When I click the "Refresh user data" button in the table toolbar
  Then the refresh button shows a loading spinner
  And the refresh button is disabled
  And the table rows update to show user ID 1050 in the current dataset
  And the filter remains "active" and the sort remains "created_desc"
  And the table remains on the same pagination page and the visible viewport still includes user ID 1011
  And a toast appears with text "Data refreshed"
  And the page shows "Last refreshed: 2025-10-24 15:00:00 UTC"

Scenario: Negative — Server error shows retryable error notification
  Given the backend returns HTTP 500 for the refresh request
  When I click the "Refresh user data" button
  Then the refresh button shows a loading spinner
  And a toast appears with text "Failed to refresh data"
  And the toast displays a visible "Retry" action button
  And the table continues to display the pre-refresh rows for users 1001..1020

Scenario: Edge — Keyboard activation (Enter / Space) triggers refresh
  Given the "Refresh user data" button has keyboard focus
  Examples:
    | Key   |
    | Enter |
    | Space |
  When I press the <Key> key
  Then the refresh button shows a loading spinner
  And the refresh button is disabled
  And a toast appears with text "Data refreshed" after the refresh completes

Scenario: Edge — Duplicate activation prevented while request in progress
  Given I have clicked the "Refresh user data" button and a refresh is in progress
  When I click the "Refresh user data" button while the refresh is still in progress
  Then the refresh button remains disabled
  And no additional success toast appears until the original refresh completes
  And only one "Data refreshed" toast appears when the original refresh finishes

Scenario: Negative — Request timeout handled with explicit timeout message
  Given the refresh request exceeds 10 seconds without a response
  When I click the "Refresh user data" button
  Then the refresh button shows a loading spinner
  And a toast appears with text "Failed to refresh data: request timed out"
  And the toast displays a visible "Retry" action button
  And the table continues to display the pre-refresh rows for users 1001..1020

Scenario: Non-functional — Refresh performance and reliability under load
  When 1,000 refresh actions are executed over 5 minutes from 50 concurrent users in the pre-agreed test environment
  Then p95 latency for refresh actions is ≤ 500 ms (measured in the pre-agreed test)
  And error rate across refresh actions is ≤ 1%