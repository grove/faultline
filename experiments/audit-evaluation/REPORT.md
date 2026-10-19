# Default Audit evaluation — 2026-10-19

Six fresh auditor contexts used the actual `faultline-audit/SKILL.md` from commit
`40cfeeafc816d5474db37cce6b014d7f7cab2ee0` through the documented direct-file
experience. Each received one synthetic repository and “find weak tests,” with
no expected answer or previous report. This is a live skill evaluation, unlike
the earlier [known-answer walkthrough](../audit-walkthrough.md).

The skill was not changed: this sample exposed no concrete behavioral problem
that justified a new instruction. Documentation now links to measured evidence.
The corpus and grading rubric provide reusable manual regression cases; offline
tests check their integrity, not future model compliance.

## Usefulness and specificity

The coordinator compared the raw reports with expectations written before the
runs. These are manual classifications against authored cases, not independently
verified facts about real repositories or model reliability.

| Case and source | Seeded expectation | Actual Audit response | Missing findings / false positives |
| --- | --- | --- | --- |
| [c01: delivery threshold](fixtures/c01) | Bug and missing assertion at exactly 50 | Identified `> 50` vs `>= 50`; add `(50, 0)` to the existing equality test. [Raw response](runs/baseline-c01.md) | 0 / 0 |
| [c02: shared assertion](fixtures/c02) | Strong threshold tests through a helper | Followed the helper and parameterized boundary cases; no actionable finding. [Raw response](runs/baseline-c02.md) | 0 / 0 |
| [c03: discount rejection](fixtures/c03) | Exception test misses mutation before validation | Identified total becoming `-10` before `ValueError`; assert unchanged cart after the exception block. [Raw response](runs/baseline-c03.md) | 0 / 0 |
| [c04: already-covered defect](fixtures/c04) | Existing test already catches the source defect | Noted that the implementation violates the contract but the existing unchanged-cart assertion would catch it; no invented weak-test finding or claim of an observed failed run. [Raw response](runs/baseline-c04.md) | 0 / 0 |
| [c05: correct retry, weak test](fixtures/c05) | Missing retry protection, not a current implementation bug | Suggested two same-key calls, one exact ledger effect, and identical receipts; explicitly classified as missing test protection. [Raw response](runs/baseline-c05.md) | 0 / 0 |
| [c06: fixture-driven retry](fixtures/c06) | Strong retry tests using a fixture | Followed both calls in the fixture and the effect/receipt assertions; no actionable finding. [Raw response](runs/baseline-c06.md) | 0 / 0 |

Observed against this rubric: **3/3 intended weaknesses identified**, **3/3
protected controls without a false positive**, and **0 missed findings**.
All three findings specified both a reachable scenario and the assertion needed
to distinguish it. These are small-case counts, not a global detection rate.

## Clarity and actionability — subjective assessment

The coordinator judged all three recommendations understandable and actionable:
each gives a concrete input, observable result, and a small edit to the existing
test style. No materially unclear explanation was flagged. This judgment comes
from the fixture author, not a developer user study or independent grader.

All six reports stated that tests were not run and named the reviewed scope.
The protected controls explained why no new test was needed rather than filling
a finding quota. c04 is particularly useful: an implementation defect and a weak
test are different questions, and this run kept them separate.

Raw response files retain the original app-local temporary links verbatim. Use
the source links in the table above for the published, portable fixture paths.

## Speed and setup — measured intervals and their limits

Each auditor sampled the UTC clock before reading and immediately before its
final response. The resulting interval includes reading, reasoning, and tool
handling, but **excludes final response generation and agent startup**. It is not
exact end-to-end user latency. Clock resolution is one second. The coordinator
also timestamped after receiving each wave's final reports, giving conservative
completion upper bounds that include final output and coordinator handling delay.

| Case | Read-to-pre-response checkpoint | Completion observed within, from first read | Read/search calls, agent-reported | Audit setup, agent-reported |
| --- | --- | --- | --- | --- |
| c01 | 11 s | 61 s | 3 | None |
| c02 | 11 s | 99 s | 3 | None |
| c03 | 9 s | 92 s | 3 | None |
| c04 | 16 s | 54 s | 6 | None |
| c05 | 10 s | 86 s | 3 | None |
| c06 | 21 s | 47 s | 4 | None |

Median checkpoint interval: **11 seconds**, range **9–21 seconds**. The upper
bounds are not actual response durations or comparable performance samples:
they include delays while the coordinator handled other work. Exact response/UI
latency, startup time, token cost, and time to a first streamed useful finding
remain unmeasured. No speed comparison with ordinary review was performed.

No auditor needed Docker, pytest installation, imports, test execution, dependency
setup, or a supplied test command. The fixture tests intentionally use pytest
syntax, but Audit only reads them. Source-read counts come from agent messages,
not independent OS telemetry; they exclude timing/orchestration calls.

Creating the isolated evaluation checkout and authoring/freezing the fixtures
took **71 seconds** (13:47:38–13:48:49 UTC). That is evaluation preparation, not
setup a developer must perform for Audit. Six audits were dispatched in two waves
of three fresh contexts; parallel scheduling is evaluation machinery, not a new
Faultline product dependency.

## Reproduce without executing fixtures

Use a fresh context in your existing coding agent for each selected case:

```text
Read /absolute/path/to/faultline/faultline-audit/SKILL.md and find weak tests
in /absolute/path/to/faultline/experiments/audit-evaluation/fixtures/c01.
```

Give the auditor only the skill and that case. Withhold
[expectations](expectations.json), other cases, and reports until grading. Read
the fixture files as data; do not import or run their tests. For timing, record
the clock before reading and label exactly which completion point is measured.
Compare the ordinary Audit response with the expected scenario/assertion afterward.

[Protocol](protocol.json), [fixture identities](fixture-manifest.json), and
[timestamps, grades, and report identities](results.json) retain the run details.
Auditors used fresh contexts and did not receive answers, but shared a filesystem;
answer isolation was instructed, not enforced by an OS access boundary. Exact
host model/version/settings and model cost were unavailable; no model override
was selected. The coordinator authored fixtures and graded reports. All runs,
including negative controls, are retained; no reruns or best-of selection occurred.

## Remaining gaps and decision

This tiny, explicit-contract sample supports keeping the current simple Audit
experience. It does not demonstrate real-repository discovery value, superiority
to ordinary direct review, repeatability, or large-repository speed. Ambiguous
contracts, absent test suites, dependency mocks, concurrency, multiple languages,
user comprehension, and adversarial repositories were not evaluated.

Keep the skill unchanged rather than invent a fix. Future evidence can justify
a narrow change and a fresh audit of the failing case. No new runner, evaluation
platform, Docker behavior, or execution capability is required.

The next proposed step is a [four-repository read-only pilot](../real-repository-evaluation-plan.md)
with independent grading and true end-to-end timing. It has not been run.

## Focused validation

Seven maintainer checks passed: four skill packaging/instruction checks, the
frozen-spike hash/syntax check, and two evaluation-data checks. The latter parse
fixture syntax and verify identities, reports, and timing/accounting consistency;
they never import or execute fixture code or rerun model audits.

The skill-creator `quick_validate.py` command failed before validation because
PyYAML (`yaml`) is missing. No package was installed and no environment was
modified. The skill itself is unchanged; its standard-library packaging checks
passed. Qualification tests were not rerun.

The execution **NO_GO / UNAVAILABLE** gate, security evidence, historical plans,
earlier experiments, and original local work remain unchanged. These source-only
audits do not qualify a sandbox or authorize project execution.
