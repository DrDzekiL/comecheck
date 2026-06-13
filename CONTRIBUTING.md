# Contributing to ComeCheck

Thanks for considering a contribution. ComeCheck is a small, local-first tool
for reviewing market alerts after they fire.

## Boundaries

Please keep the project boring and safe:

- Do not add trading signals.
- Do not add order placement.
- Do not add exchange account APIs.
- Do not add private key or credential handling.
- Do not add financial advice language.
- Do not include real personal trading data in examples.

## Local Setup

```bash
git clone https://github.com/DrDzekiL/comecheck.git
cd comecheck
pip install -r requirements.txt
streamlit run app.py
```

The app stores local user data in `data/alerts.jsonl`. That file is ignored by
Git. Sample data lives in `examples/sample_alerts.jsonl`.

## Good First Contributions

- Improve README clarity.
- Add sample replay workflows.
- Improve Markdown export formatting.
- Add CSV export.
- Add tests for JSONL helpers.
- Improve labels, empty states, and accessibility.

## Pull Request Checklist

- Keep user data out of commits.
- Keep examples generic.
- Keep the no-signals/no-orders boundary intact.
- Update docs when behavior changes.
- Prefer small focused pull requests.
