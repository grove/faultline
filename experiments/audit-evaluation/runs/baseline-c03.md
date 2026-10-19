### Invalid discounts change the cart before raising

- **What could go wrong:** With `{"total": 100}` and discount `110`, [apply_discount](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c03/cart.py:2>) changes the total to `-10` before raising `ValueError`. This violates the [requirement](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c03/README.md:4>) that invalid discounts leave the cart unchanged.
- **Why these tests may miss it:** [test_invalid_discount](</private/tmp/faultline-audit-eval.s5nr9gdv/experiments/audit-evaluation/fixtures/c03/test_cart.py:12>) checks only the exception, allowing the unwanted mutation.
- **Smallest useful test:** Add `assert cart == {"total": 100}` after the existing `pytest.raises` block.
- **Confidence and uncertainty:** High-confidence **suspected implementation bug**, supported by the explicit contract and assignment order. This is source inspection, not a reproduced failure.

Reviewed scope: the fixture’s README, implementation, and both tests. Runtime behavior was not verified. **Tests were not run.**
