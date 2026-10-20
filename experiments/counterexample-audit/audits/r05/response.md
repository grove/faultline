**1. Skip-marked custom items can fail during reporting**

**What could go wrong:** A custom `Item` can inherit [`reportinfo()` returning `line=None`](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/nodes.py:654). When a skip marker triggers, the [report hook asserts that the line exists](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/skipping.py:294), turning an ordinary skip into a reporting failure.

**Why these tests may miss it:** The [custom-item test covers xfail](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:1139), which bypasses this branch. The [skip-location test](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:1193) uses a Python function with a known line number.

**Smallest useful test:** Reuse the custom `MyItem` collector, attach a skip marker during collection, and leave `reportinfo()` inherited. Assert one skipped result, the supplied reason, and no internal error. Allow a fallback location.

**Confidence and uncertainty:** High-confidence **suspected implementation bug**: the base API explicitly permits an absent line number.

**2. `--runxfail` still evaluates xfail conditions**

**What could go wrong:** The [call hook evaluates xfail marks before checking `runxfail`](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/src/_pytest/skipping.py:247). A passing test marked `xfail("1 / 0")` can therefore fail before its body executes, despite the [documented promise to run and report it as unmarked](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/doc/en/skipping.rst:351).

**Why these tests may miss it:** The [`--runxfail` test](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:222) uses an unconditional marker and an imperative call. The [invalid-condition tests](/private/tmp/faultline-counterexample-evaluation/stage/c06/project/testing/test_skipping.py:894) omit that option.

**Smallest useful test:** Mark a passing test `xfail("1 / 0", run=False)`, then invoke it with `--runxfail`. Assert that its body executes, its call report passes without `wasxfail`, and the exit status is zero.

**Confidence and uncertainty:** High-confidence **suspected implementation bug**, supported by the explicit option contract; not reproduced.

Reviewed the supplied marking, execution, reporting, custom-item, test, fixture, and documentation paths. Findings are limited to static inspection of those files. **Tests were not run.**
