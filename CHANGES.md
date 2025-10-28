# CHANGES

## 0.6 (unreleased)

- Getting a title now always uses the reference page.
- Updating attributes of a title is now achieved through setters.
- Improve GraphQL handling.
- Credits now contain person objects instead of subclassing.
- Add Accept-Language header to HTTP requests (@tykling).

## 0.5.1 (2025-10-14)

- Fix imports for cli and tests.

## 0.5 (2025-10-14)

- Drop support for Python 3.10.
- Remove the title main page parser.
- Adjust reference page for changes in credit categories.

## 0.4 (2025-07-25)

- Change license to GPL v3 or later.
- Add parser for new title reference pages.
- Add support for parsing parental guide pages (@mhdzumair).
- Switch to uv for project management.

## 0.3 (unreleased)

- Add support for extracting data from GraphQL (@mhdzumair).
- Add support for parsing alternative titles (@mhdzumair).
- Add support for parsing series creators.
- Make TV mini-series compatible with series.

## 0.2 (unreleased)

- New page parser: episodes.
- Added title data: plot summaries, top/bottom ranks.
- Updating titles now updates in-place.

## 0.1a20240105 (2024-01-05)

- Title parser with basic information, cast, crew, and taglines.
