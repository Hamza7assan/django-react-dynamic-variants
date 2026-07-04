Architecture & Design Decisions

This document outlines the core architectural choices made to satisfy the dynamic requirements of the E-Commerce Variants system, prioritizing data integrity, safety, and performance.

1. Data Model & Combination Storage

Decision: I opted for a normalized relational approach (PostgreSQL/SQLite) with an eager-generation strategy rather than NoSQL or lazy-generation.

The "Smart Sync" Algorithm: When an admin modifies variant types or options, the refresh_combinations() method is triggered. Instead of blindly deleting and recreating all combinations (which would wipe out custom pricing and stock data), the algorithm calculates the Cartesian Product (itertools.product) of all current options.

It preserves mathematically valid existing combinations, safely archives obsolete ones, and creates only the newly introduced ones.

Lookup Strategy: The React frontend passes an array of selected option_ids. The backend finds the exact combination via strict M2M relational checks. By ensuring the combinations table is always mathematically accurate, frontend lookups remain $O(1)$ fast.

2. Inventory Atomicity & Concurrency

Decision: To prevent race conditions and overselling, the checkout process utilizes strict database-level locking.

The order creation logic is wrapped in Django's transaction.atomic().

I implemented Pessimistic Locking using .select_for_update() on the Combination row. This ensures that if two users attempt to purchase the last remaining item simultaneously, the database forces them into a queue, processing one transaction fully before allowing the next to read the stock.

3. Historical Data Integrity (Soft Archiving)

Decision: Allowing the deletion of an option (e.g., 'Color: Red') that was part of a previously fulfilled order corrupts historical accounting data.

I enforced on_delete=models.PROTECT on the Order-Combination relationship.

If an admin forcefully deletes an option, the system catches the ProtectedError. Instead of crashing or returning a 500 error, it performs a Soft Archive—reducing the stock of the affected combination to 0 and hiding it from the frontend, while maintaining the record for past invoices.

4. Frontend Dynamic Architecture

Decision: The React storefront must remain 100% agnostic to variant names and structures.

The UI dynamically maps over the variant_types provided by the API endpoint.

It utilizes a reactive useEffect hook. The moment the user's selected keys match the total available variant types for that product, an API call is fired to resolve the combination, updating the final price and stock dynamically without requiring a form submission.

For simple products (e.g., a basic Mug with zero variants), the frontend intelligently sends an empty array to match the backend's default SKU fallback.