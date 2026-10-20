1. **Skipping a custom item can break report generation**

   **What could go wrong:** A custom `Item` inherits a valid default [`reportinfo()` returning `None` for its line number](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/src/_pytest/nodes.py:654). Apply a skip marker before setup: skipping succeeds, but [report rewriting asserts that the line exists](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/src/_pytest/skipping.py:295), raising `AssertionError` instead of returning the skip report.

   **Why these tests may miss it:** [Skip-location tests use Python functions](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:251). The [custom-item marker test exercises xfail](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:1164), which bypasses this location-rewriting branch.

   **Smallest useful test:** Reuse the [custom YAML collector fixture](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/conftest.py:106), add a skip marker during collection, and request `-rs`. Assert one skipped item, the supplied reason, exit status zero, and no body execution. Allow reporting without a line number.

   **Confidence and uncertainty:** High-confidence **suspected implementation bug**. The base API explicitly permits an absent line number; no restriction on skipping such items appears in the supplied files.

2. **`--runxfail` still evaluates conditions that can prevent execution**

   **What could go wrong:** With `--runxfail`, setup bypasses xfail evaluation, but the [call hook evaluates markers before checking the option](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/src/_pytest/skipping.py:247). An xfail string condition that raises therefore prevents the test body from running and produces a failure. This contradicts the [documented behavior of running and reporting as though unmarked](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/doc/en/skipping.rst:351).

   **Why these tests may miss it:** The [override test uses an unconditional marker](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:222). [Condition-error tests use ordinary execution](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:919), leaving their interaction uncovered.

   **Smallest useful test:** Use `testdir.makepyfile` to create a passing test marked with `xfail("condition_probe()")`, where the probe raises if evaluated. Invoke `--runxfail`; assert the body executes, one ordinary pass, and exit status zero.

   **Confidence and uncertainty:** High-confidence **suspected implementation bug** against the documented override policy. An intentional exception requiring condition validation would need clarification in that contract.

Reviewed the supplied marker implementation, runner, reporting code, node APIs, tests, fixtures, and skipping documentation. Findings are based on source inspection; runtime behavior was not verified. **Tests were not run.**
