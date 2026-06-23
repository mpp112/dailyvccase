# AGENTS.md

## Mission

Build and maintain a provenance-first research workflow for overseas VC financing cases, Chinese comparables, financing histories, and investor analysis.

## Non-negotiable rules

1. Never invent financing amounts, valuations, revenue, customer counts, growth rates, investors, dates, or citations.
2. Distinguish Fact (`F`), Signal (`S`), and Hypothesis (`H`).
3. Every critical fact must point to one Tier-1 source or two independent Tier-2 sources.
4. Preserve conflicts; do not silently choose one source.
5. Keep original currency and original wording. Currency conversion is secondary and must include the FX date.
6. Do not infer a financing event solely from shareholder, registered-capital, employee-option-pool, or legal-structure changes.
7. Do not call a Chinese company a direct comparable unless its score is at least 75/100.
8. Never bypass logins, CAPTCHAs, paywalls, access controls, robots rules, or source terms.
9. Do not store secrets or unnecessary personal data.
10. Publishing always requires a human approval state.

## Engineering conventions

- Prefer Python with type hints and Pydantic models.
- Use deterministic code for validation, normalization, scoring, and rendering.
- Keep LLM-generated analysis separate from verified facts.
- Store raw, normalized, and rendered data in separate directories.
- Make ingestion idempotent.
- Use ISO dates and UTF-8.
- Write small functions and explicit errors.
- Add or update tests for every behavior change.
- Run formatter, linter, type checker, unit tests, and smoke test before declaring completion.

## Required commands

The completed project should expose equivalent commands for:

- discover candidates;
- ingest a URL or structured file;
- create/open a case;
- normalize entities;
- score candidates;
- add and validate claims;
- rank Chinese comparables;
- validate a case;
- render a daily memo;
- generate weekly review data.

## Work method

- Inspect the repository first.
- Write a short implementation plan before editing.
- Make sensible defaults and record assumptions instead of blocking on questions.
- Work in small, reviewable commits.
- Never mark work complete until commands and tests have actually run.
- When a live source or credential is unavailable, implement an adapter interface, fixture, and clear setup note rather than fabricating a successful integration.
