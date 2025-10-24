Story ID: STORY-0003
Feature: Customer dashboard provides immediate visibility of orders, shipments, spending and notifications
Actor/Role: Customer
Goal/Benefit: Provide customers immediate visibility of recent orders, shipment status, total spending, and notifications so they can find key information without contacting support.
Out of scope:
- Order cancellation/returns flows
- Full order history beyond the last 90 days

AC-1: Recent orders, spending and notifications display
Given the user "alice@example.com" is authenticated and in timezone "UTC"
And the account has 3 recent orders:
  - ORD-1001 (2025-10-20T10:00:00Z, $120.00, tracking TRK123456789, status "Delivered")
  - ORD-1002 (2025-10-18T08:00:00Z, $45.50, tracking TRK987654321, status "In transit")
  - ORD-1003 (2025-10-15T12:00:00Z, $200.00, tracking TRK555666777, status "Delayed")
And the account has 2 unread notifications
When the user navigates to the dashboard page
Then the Recent Orders list displays three entries in descending date order: ORD-1001, ORD-1002, ORD-1003
And the Spending tile displays "$365.50"
And the shipment badges for ORD-1001, ORD-1002 and ORD-1003 display texts "Delivered", "In transit", "Delayed" respectively
And the notifications indicator displays "2"

AC-2: Shipment status and tracking details (Examples)
Given an order ORD-2001 exists with tracking number "TRK123456789" and status "<TrackingStatus>"
When the user opens order ORD-2001 details on the dashboard
Then the shipment status badge displays "<BadgeText>"
And the tracking number text displays "Tracking: TRK123456789"
And the shipment detail line displays "<DetailVisible>"

Examples:
| Case | TrackingStatus | BadgeText   | DetailVisible                    |
|------|----------------|-------------|-----------------------------------|
| 1    | delivered      | Delivered   | Delivery date: 2025-10-20        |
| 2    | in_transit     | In transit  | Carrier: FastShip                |
| 3    | delayed        | Delayed     | Estimated delivery: 2025-10-25   |

AC-3: Expired session shows login prompt
Given the user's authentication token is expired
When the user navigates to the dashboard page
Then a modal dialog appears with exact text "Session expired. Please log in again."
And the login page is displayed

AC-4: Export spending CSV fails with network error
Given the account has at least one order
When the user clicks the "Export spending CSV" button on the dashboard
Then a toast appears with exact text "Export failed: Network error"
And no file download starts

AC-5: No recent orders displays empty state and CTA
Given the account has zero orders in the last 90 days
When the user navigates to the dashboard page
Then the Recent Orders area displays exact text "You have no recent orders"
And a "Browse products" call-to-action button is visible

AC-6: Dashboard load latency under concurrent load (non-functional)
When 100 concurrent authenticated users load the dashboard page (representative action under test)
Then p95 latency is ≤ 400 ms (measured in pre-agreed test environment)
And error rate is ≤ 1%