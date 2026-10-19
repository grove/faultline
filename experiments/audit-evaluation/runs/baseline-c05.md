### Same-key retry behavior has no test protection

- **What could go wrong:** A regression in [`Checkout.charge`](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c05/checkout.py:15>) could record a second ledger effect or return a different receipt when the same key and amount are retried.
- **Why these tests may miss it:** [`test_first_charge`](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c05/test_checkout.py:4>) calls `charge` only once. It would still pass if every call recorded a fresh effect.
- **Smallest useful test:** Call `charge("order-1", 1250)` twice on the same checkout. Assert both receipts equal `"receipt-1"` and `ledger.effects` remains exactly `[("order-1", 1250)]`.
- **Confidence and uncertainty:** High confidence in **missing test protection**, not an observed implementation bug. The current cache appears to meet the sequential retry contract stated in the [README](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c05/README.md:3>).

Reviewed the README, implementation, and supplied test. Other keys, changed amounts, restarts, concurrency, and lost acknowledgements were outside scope. **Tests were not run.**
