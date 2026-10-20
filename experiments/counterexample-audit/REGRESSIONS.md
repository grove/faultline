# Counterexample regression checks

These are maintainer checks, outside ordinary Audit. Read source as data; never
execute the target or a proposed test. The canonical skill still returns its
four existing finding fields and keeps execution **NO_GO / UNAVAILABLE**.

## Known packaging mechanism: separate the policy guard from the comparator

This answer is already known. It explains the reasoning change and checks that
the mechanism can be applied; it is **excluded from the held-out comparison**.
The historical correction is [packaging PR #794](https://github.com/pypa/packaging/pull/794).
Neither recalling that fix nor finding it again is unbiased detection evidence.

Use packaging commit `a716c52b5f3ca9b4a512f538b80ced8ee01b2775`, the unchanged
43-file [prior source manifest](../packaging-2x2/source-manifest.json), and the
[historical PEP](../packaging-2x2/specification/pep-0440.rst) at python/peps commit
`d55eeb1958a4698b7f1fd482d424be869634f1a6`. The PEP's exclusive-comparison rule
permits earlier prereleases when the bound is itself a prerelease. Its general
prerelease policy permits explicitly requested prereleases. Interpret these
together; do not elevate the existing test oracle over them.

Source-only trace for candidate `3.0.0a7` and bound `<3.0.0a8`:

| Entry/policy | Full decision path in this snapshot | Contract expectation |
| --- | --- | --- |
| Default `contains(candidate)` | `None` selects `self.prereleases`; detection omits `<`; false policy plus prerelease candidate returns `False` before comparison. | `True` under the explicit-prerelease-bound rule. |
| `contains(candidate, prereleases=True)` | Bypasses detection; guard allows candidate; comparator sees an earlier candidate and a prerelease bound, so returns `True`. | `True`. |
| `contains(candidate, prereleases=False)` | Explicit exclusion makes the guard return `False`. | `False`; explicit exclusion is a separate supported mode. |
| Candidate `3.0.0a7`, bound `<3.0.0`, forced inclusion | Reaches comparator, which excludes prereleases of that same final release. | `False`; mode differences alone do not establish a bug. |

`Specifier.__contains__` delegates to default `contains`; its default policy is
therefore relevant too. Do not transfer this expectation indiscriminately to
`installed=True`, resolver fallback, or every `SpecifierSet.filter` policy.

`tests/test_specifiers.py::TestSpecifier.test_specifiers` constructs
`Specifier(spec, prereleases=True)` before its assertions. Those broad comparisons
cannot check the omitted autodetection path. The separate autodetection table
even expects `False` for `<1.0.dev1` and `>1.0.dev1`: existence of a policy test
does not make its oracle authoritative. The smallest useful regression suggestion
is default membership below the explicit prerelease bound, with explicit inclusion
and exclusion as neighboring controls. No proposed test was executed.

With the normative document withheld, the source tension still merits a concise
contract question: if an explicit prerelease bound opts in, require default
membership; if policy intentionally requires a separate opt-in, require exclusion
and explain that restriction. A comparator exception alone does not settle policy.

## What the automated checks protect

The archive checks bind the tested skill to the shipped bytes, preserve both
execution fences, enforce identical source/settings within each paired audit,
and reconcile complete-response timings and all graded claims. They retain
misses, unsupported claims and failed sessions. These are evidence-integrity
checks, not a semantic test that future free-form audits must pass.

The fresh known-case response, held-out outcomes and limitations belong in
[REPORT.md](REPORT.md). Prior PR #20/#21 reports and their historical misses remain
unchanged. No outcome in this experiment retroactively changes those results.
