# Cyber Log Analyzer Development Guide

## Project Purpose

Cyber Log Analyzer is a learning project for building a tested,
deterministic security-log analysis agent.

## Project Structure

- `src/cyber_log_analyzer/agents/`: agent state, decisions, tools, registry,
  tool selection, and agent loop
- `src/cyber_log_analyzer/analyzers/`: security analysis logic
- `src/cyber_log_analyzer/parsers/`: log parsing
- `src/cyber_log_analyzer/readers/`: file reading
- `src/cyber_log_analyzer/reporters/`: report generation
- `src/cyber_log_analyzer/web/`: Flask web interface
- `tests/`: automated tests

## Development Rules

- Use test-driven development for new behavior.
- Write or update a focused test before implementation.
- Run the focused test first.
- Run the full test suite after the focused test passes.
- Preserve existing behavior unless the task explicitly changes it.
- Do not add production dependencies without explaining why.
- Keep agent decisions, tool execution, and state management separate.
- Do not hide errors; represent expected failures through structured results.
- Prefer small, reviewable changes.

## Verification

Run the full test suite with:

```powershell
python -m pytest -q