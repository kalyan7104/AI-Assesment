# Evaluation Results

This directory is populated when you run the evaluation script:

```bash
python src/evaluation/run_evaluation.py
```

## Output Files

| File | Contents |
|---|---|
| `results_test_tickets.json` | Results for standard test cases |
| `results_tricky_test_tickets.json` | Results for edge-case / tricky test cases |
| `results_summary.json` | Combined summary across both files |

## Metrics Reported

| Metric | Description |
|---|---|
| Citation coverage rate | % of responses containing at least one `POL-XXX` citation |
| Unsupported claim rate | Average number of unsupported claim flags per test |
| Correct escalation rate | % of escalation-expected cases correctly escalated |
| Correct "needs info" rate | % of ambiguous cases correctly requesting more information |
| Success rate | % of tests that passed (cited + non-error status) |

## Test Cases

- `data/test_cases/test_tickets.json` — 15 standard scenarios (returns, shipping, payments, etc.)
- `data/test_cases/tricky_test_tickets.json` — edge cases (policy conflicts, exceptions, ambiguous inputs)
