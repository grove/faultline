Found two actionable gaps from source inspection.

**1. A cached inherited xfail can bypass a fixture’s `run=False` marker**

- **What could go wrong:** An active module-level xfail is cached during setup. A fixture then adds an item-level `xfail(run=False)`, but the [call hook](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/src/_pytest/skipping.py:248) refreshes only a `None` cache. The body can therefore execute despite the new restriction—significant because [`run=False` is documented for tests that could crash the interpreter](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/doc/en/skipping.rst:310).
- **Why these tests may miss it:** [The dynamic no-run test](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:400) starts without an existing xfail, so its cache is `None` and refresh succeeds. It never exercises replacement of an active inherited mark.
- **Smallest useful test:** Extend that test with a module-level `pytestmark = pytest.mark.xfail(reason="existing")`. Have the fixture add `xfail(run=False, reason="unsafe")`, and have the body create a sentinel file. Assert the file is absent and reporting includes `XFAIL` and `[NOTRUN] unsafe`. Fixture setup itself should still execute.
- **Confidence and uncertainty:** **Suspected implementation bug, medium-high confidence.** [Marker iteration](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/src/_pytest/nodes.py:302) places item markers before inherited markers, supporting this expectation. An intentional policy freezing the first active xfail would change the expectation, but that policy is not stated in the supplied documentation.

**2. `--runxfail` still evaluates conditions and can prevent execution**

- **What could go wrong:** Setup correctly avoids xfail evaluation under `--runxfail`, but [the call hook evaluates marks before checking the option](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/src/_pytest/skipping.py:249). A marker such as `xfail("1 / 0", reason="legacy condition")` can therefore fail before a passing body runs. This conflicts with the [documented behavior of running and reporting as though unmarked](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/doc/en/skipping.rst:351).
- **Why these tests may miss it:** [The run-anyway test](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:222) uses an unconditional marker. [Condition-error tests](/private/tmp/faultline-counterexample-evaluation/stage/c03/project/testing/test_skipping.py:919) exercise normal execution without `--runxfail`.
- **Smallest useful test:** Use `testdir` to create a passing test with that string condition and a body sentinel. Run with `--runxfail`; assert the sentinel exists, one ordinary pass, zero exit status, and no xfail classification.
- **Confidence and uncertainty:** **Suspected implementation bug, high confidence.** The option check occurs after condition evaluation; runtime behavior remains unverified.

Reviewed the supplied skip/xfail implementation, runner, marker ordering, report creation, terminal reporting, tests, fixtures, and skipping documentation. Findings are limited to the supplied snapshot; no code execution, network access, or edits occurred. **Tests were not run.**
