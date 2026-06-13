# ComeCheck Roadmap

ComeCheck is intentionally small: a local-first alert replay journal, not a
trading bot, signal service, exchange integration, or AI trading assistant.

## MVP

- Manual alert event entry
- Local JSONL storage
- Pending review queue
- Verdict tagging
- Lesson and rule update fields
- Dashboard counters
- Markdown export for a selected alert
- Sample alerts for local testing

## Next

- CSV export
- Better Markdown export formatting
- Import sample alerts from JSONL
- Optional screenshot attachment path per alert
- More example replay workflows in the docs
- Basic automated tests for JSONL read/write helpers

## Later

- Optional TradingView webhook JSON import
- Search and filter by asset, verdict, tag, and date
- Lightweight charts from uploaded screenshots or manual notes
- Multiple local journals
- Accessibility pass for Streamlit layout

## Non-Goals

- No trading signals
- No order placement
- No exchange account APIs
- No private keys
- No broker integration
- No cloud sync by default
- No financial advice
- No automated entry or exit recommendations
