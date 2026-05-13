# Feature Proposals (No UI/Structure Changes)

This document lists safe, additive features for the Pokemon database course project that can be implemented mostly in backend/query/template logic without redesigning the existing structure.

## 1) Advanced Search Presets
- Add saved query shortcuts (e.g., "High HP", "Rare + Market Price", "By Artist").
- Keep existing card list page and filters; only add preset links that map to existing query params.
- Demonstrates query composition and usability.

## 2) Data Quality Dashboard Widgets
- Show counts of:
  - cards missing `hp`
  - cards missing `rarity`
  - cards without `price`
  - sets with 0 cards
- Can be added to existing dashboard as extra metrics.
- Demonstrates data validation and completeness tracking.

## 3) Set Comparison View
- Compare 2 sets side-by-side:
  - number of cards
  - average HP
  - rarity distribution
  - top 5 most expensive cards
- Reuses existing models and aggregates.
- Demonstrates GROUP BY/aggregation skills.

## 4) Type Effectiveness Summary
- For each Type, show:
  - how often it appears as card type
  - most common weakness against it
  - most common resistance against it
- Uses joins across `CardType`, `Weakness`, `Resistance`, `Type`.
- Strong database/reporting feature for professor evaluation.

## 5) Price Trend Snapshot
- Add a lightweight historical table (`card`, `date`, `market_price`) populated during imports.
- Show 7-day or 30-day trend direction on card detail (up/down/flat).
- No redesign needed; simple indicator text/icon is enough.
- Demonstrates temporal data modeling.

## 6) "Collection Insights" Queries
- Add backend-only analytics endpoints/pages such as:
  - top artists by card count
  - average price by rarity
  - average HP by type
  - cards with highest attack converted cost
- Mostly ORM aggregations and templates.
- Excellent for database-course grading.

## 7) Duplicate/Anomaly Detection
- Add checks for suspicious records:
  - same name + set + number duplicates
  - negative/zero impossible values
  - attack rows without names
- Render results in admin/report page.
- Demonstrates constraints, cleaning, and integrity checks.

## 8) Export Reports from Live DB
- Add CSV export for currently filtered card list and set list.
- Reuses existing filters; adds a `?format=csv` branch in view.
- Demonstrates practical DB extraction use-case.

## 9) Import Job Log
- Track each import run with:
  - start/end time
  - pages fetched
  - created/updated/errors
- Display log table in dashboard/admin.
- Demonstrates operational metadata management.

## 10) "Professor-Friendly" SQL Showcase Page
- Add one page listing 6–10 meaningful SQL/ORM queries and their output.
- Example categories: joins, aggregates, grouping, filtering, ranking.
- Great for demonstrating database depth without UI redesign.

---

## Suggested Priority Order (Fastest Value)
1. Data Quality Dashboard Widgets
2. Collection Insights Queries
3. Export Reports from Live DB
4. Set Comparison View
5. Import Job Log

These provide visible, measurable database functionality while preserving current structure/design.
