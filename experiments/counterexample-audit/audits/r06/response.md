**1. Skipping a custom Item can fail during reporting**

**What could go wrong:** A custom `Item` inherits a valid [`reportinfo()` default with no line number](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/nodes.py:654). If it receives a skip marker before setup, skip reporting reaches [`assert line is not None`](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/skipping.py:303). Reporting can therefore raise an internal error instead of recording the skip.

**Why these tests may miss it:** The [custom Item test](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:1139) exercises xfail, which takes a different reporting branch. It never applies skip to an Item without a source line.

**Smallest useful test:** Reuse that custom collector, attach `pytest.mark.skip(reason="unsupported")` during collection, and retain the inherited `reportinfo()`. Assert one skipped result, no internal error, and no execution of `runtest()`. Allow reporting to omit the unavailable line.

**Confidence and uncertainty:** High-confidence **suspected implementation bug**: the assertion conflicts with the base Item’s supported default. Runtime behavior remains unverified.

**2. `--runxfail` still evaluates xfail conditions**

**What could go wrong:** With `@pytest.mark.xfail("1 / 0", reason="ignored")`, `--runxfail` bypasses evaluation during setup, but the [call hook evaluates the condition before checking the option](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/skipping.py:247). That exception can prevent a passing test body from running. The [documented policy](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/doc/en/skipping.rst:351) says the test runs and reports as though unmarked.

**Why these tests may miss it:** [`test_xfail_run_anyway`](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:222) uses an unconditional marker. The [expression-error test](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:894) runs without `--runxfail`.

**Smallest useful test:** Add a passing test with the condition above and a body-execution sentinel. Run through the existing `testdir` harness with `--runxfail`; assert the body executed, one ordinary pass, and exit status zero.

**Confidence and uncertainty:** High-confidence **suspected implementation bug**, supported by the documented override and the misplaced guard. This was traced statically, not reproduced.

**3. `--runxfail` bypasses ordinary skip-location correction**

**What could go wrong:** For a normal `skipif(True, reason="unsupported")` test, the [`runxfail` reporting branch](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/skipping.py:273) bypasses the later correction that points skips at the test definition. Consequently, `-rs` can identify pytest’s internal skip site instead of the skipped test.

**Why these tests may miss it:** [`test_skipif_reporting`](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:668) checks the test filename only without `--runxfail`.

**Smallest useful test:** Parameterize that reporting test with and without `--runxfail`. Require the same test filename, source line, reason, and skipped outcome in both modes.

**Confidence and uncertainty:** High-confidence **suspected reporting bug**. The correction’s own comment establishes the intended location; exact terminal output remains unverified.

Reviewed the supplied marking logic, relevant runner/reporting callers, focused tests and fixtures, and skipping documentation. Findings are limited to static inspection of the supplied files. **Tests were not run.**
