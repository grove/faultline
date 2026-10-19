### Free-delivery threshold excludes exactly 50

- **What could go wrong:** A total of 50 is charged 5 because [delivery_cost uses `> 50`](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c01/quote.py:2>). The [documented contract](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c01/README.md:4>) makes delivery free at 50 or above.
- **Why these tests may miss it:** The [parameterized test](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c01/test_quote.py:6>) checks 0, 49, and 51, skipping the exact threshold. Those cases cannot distinguish `>` from `>=`.
- **Smallest useful test:** Add `(50, 0)` to the existing parameter list, retaining the same equality assertion.
- **Confidence and uncertainty:** High-confidence **suspected implementation bug**, supported by the explicit README requirement. A different authoritative threshold contract would refute it; source inspection alone does not reproduce it.

Reviewed scope: delivery-price requirements, implementation, and the supplied test file. Other pricing and validation behavior were outside scope. **Tests were not run.**
