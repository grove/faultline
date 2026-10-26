# Faultline implementation plan

**Current priority:** useful read-only Audit in minutes. Execution remains
**NO_GO / UNAVAILABLE**. Docker verification is a proposed later capability,
not an enabled mode or approval to change the existing authorization boundary.

## 1. Ship the Audit experience

Keep one canonical `faultline-audit/SKILL.md`. Change the skill, README, design,
implementation plan, and packaging/instruction checks together. No runtime,
dependency, service, CLI, additional skill, or sibling integration is needed.

- Accept a repository or paths; infer supported behavioral promises from code,
  documentation, and callers before looking for weak assertions or mutations.
- Use the Critical Failure Challenge Loop internally: consider credible failures,
  prioritize severity, plausibility, detection weakness, and actionability, then
  trace safeguards and tests and actively seek evidence that refutes each concern.
- Read files as data without imports, discovery, tests, builds, scripts, Docker
  inspection, installs, or edits.
- Return up to three realistic, source-linked findings ordered by consequence and
  confidence. Explain the consequence and why tests could miss it; propose the
  smallest independently meaningful assertion or repeatable regression test.
  Distinguish suspected bugs, missing test protection, and unresolved contract
  questions. Say that tests were not run.
- Allow no actionable finding with a scope and reason. Do not invent a guarantee,
  measured coverage, reproduced failure, or passing test result.
- Keep available candidate identity internally. Remove mutation protocols,
  qualification procedures, hashes, and accounting from ordinary reports.
- Explain that verification is not enabled and suggest a test. Retain the execution
  refusal and host/tool qualification plus caller-authorization requirements.

Acceptance: direct-file use and standalone copying need no setup; packaging,
links, report essentials, and execution refusal remain checked. Use read-only
walkthroughs too: instruction checks alone cannot prove an agent follows the
skill. Packaging success is not proof of usefulness.

The [initial source-only walkthrough](experiments/audit-walkthrough.md) records
two known historical bugs, a clean control, and execution-refusal checks. It is
retrospective and not an independent effectiveness benchmark.

The [six-case live skill evaluation](experiments/audit-evaluation/REPORT.md) now
records fresh-context audits of synthetic weak/strong test pairs, withheld answers,
raw reports, measured clock intervals, and manual grading. All three intended
weaknesses were identified without false positives on the three protected
controls. No skill change was justified. The fixtures are reusable manual
regression cases; offline checks preserve evidence and do not test model compliance.
Real-repository value, independent grading, repeatability, and exact end-to-end
latency remain unestablished.

The [six impact-first cases](tests/fixtures/impact-first.json) add authored
regression expectations for acknowledgement before durability, complete recovery
protection, integrity before formatting, unsettled contracts, fabricated errors,
and no meaningful finding. Offline maintainer checks parse these packets as data;
they do not execute fixture code or observe an agent following the revised skill.
The archived counterexample trial stays bound to its frozen instruction hashes,
not byte equality with the evolving live skill. All historical records remain
unchanged; the current execution fences remain byte-identical.

## 2. Preserve research; retire its build order

Leave `ISOLATION.md`, `qualification/`, terminal receipts, frozen experiments, and
their tests intact, including prior local/uncommitted work. Keep the execution
decision unchanged. No startup, provisioning, calibration, guest launch, cleanup,
or qualification rerun follows from this product change.

Retain the previous [design](DESIGN-HISTORY.md) and
[implementation plan](IMPLEMENTATION-HISTORY.md) as explicitly historical documents.
They preserve the NARROW decision, controls, evidence semantics, costed comparison,
and issue map. Relative cross-links point to the historical documents; research
content is retained. Existing issues are not updated, closed, or reinterpreted as
passed gates by this local implementation.

Custom VM, QEMU, Firecracker, further Apple Container qualification, and mutation
backend work are deferred. Historical “next authorization” procedures are not the
current roadmap and grant no new effects.

## 3. Check that Audit helps

Read a few public historical pre-fix source/test snapshots and clean controls as
data. Retain source links, reviewed assertions, concrete test suggestions or a
justified no-finding result, uncertainty, and any observed time/cost. Never execute
those repositories or their examples.

Label answer leakage in known-answer walkthroughs. Do not claim independent bug
discovery or speed improvement. A later independent comparison should assess
useful findings, false positives, developer effort, and time to a useful test
against ordinary direct review. Do not build a benchmark harness or make
unmeasured effectiveness claims.

Prepare [RO-1: ordinary review versus Faultline](experiments/ordinary-review-comparison/PROTOCOL.md)
as a separately tracked read-only phase: six prepared candidate scopes, matched
budgets and an all-outcomes results sheet. The sole human serves as curator and
grader by explicit instruction; keep those roles separate from audit workers and
disclose selection bias. This draft is **NOT FROZEN / NOT RUN**. Qualify existing
budget enforcement and complete case curation/configuration, then obtain
explicit approval of the frozen bundle and finite budget before any model
dispatch. No new runner, schema, or AI reviewer is needed. Preserve
issue #6's original #4/#5 dependencies and #2 safety gate for its conditional
executable study; RO-1 does not complete those acceptance criteria.

**Impact-first improvement hypothesis — unmeasured:** the
[counterexample trial](experiments/counterexample-audit/REPORT.md) supplied a small
positive signal for full-path tracing, which this change retains. The
[packaging comparison](experiments/packaging-2x2/REPORT.md) still missed its target
and retained unsupported policy assertions; more instructions alone did not
establish better reasoning. The later [two-case ordinary-review pilot](experiments/ordinary-review-comparison/PILOT-RESULTS.md)
reported **NO CLEAR BENEFIT**, with human grading pending. Its observer noted
concrete failure hooks and careful uncertainty in Faultline's reports, but no
unique weakness. The hypothesis is that explicitly selecting supported promises
and ranking consequences will direct limited attention toward more consequential,
independently defensible test gaps while preserving those strengths.

No new model evaluation is performed by this implementation. After separate
approval of a concrete comparison and finite budget, compare the previous and
revised skill with ordinary review on the same source packets. Withhold authored
expectations from reviewers; retain all first responses and assess consequential
defensible gaps, false positives and unsupported claims, clarity, latency/cost,
recognition of protected behavior, and conditional treatment of unclear contracts.
The six new examples are reviewable expectations, not measured results or held-out
evidence. Preserve all prior experiments. Do not claim better detection, accuracy,
clarity, speed, or cost without measurements; prefer the simpler instructions if
the added reasoning shows no meaningful benefit.

## 4. Separately review Docker scope before implementation

No Docker launcher is part of this change. Before adding or enabling one, obtain
a separate, explicitly reviewed scope change and approval covering the narrower
trusted-repository threat model and its relationship to the existing NO-GO gate.
A “verify” request, repository trust, or installed Docker is insufficient.

That review must make the [proposed Docker contract](DESIGN.md#optional-verify-with-docker--proposed-disabled)
concrete: local prerequisites, snapshot/command-bound opt-in, staging/link handling,
no original/sensitive host mounts, no network, unprivileged execution, enforceable
resource/storage limits, independent evidence, timeouts, cleanup, clear attribution,
and residual-risk wording. Missing controls mean unavailable, not a weaker fallback.

Only after that approval, implement one Python workflow using existing Docker and
test tools. Test staging escapes/secrets, launch policy, output bounds, receipt
protection, prerequisite failures, baseline failure, attribution, timeout, drift,
and interrupted cleanup. Docker remains unsuitable for arbitrary hostile code.
No pluggable backend layer, automatic dependency repair, or sandbox platform.

Per-run user approval remains necessary after the feature itself is approved and
enabled; enabling it does not authorize a repository or command.

## Bounded first comparison (PROPOSED — NOT RUN)

Historical links, including the frozen spike, retain this entry point. The
[original costed comparison](IMPLEMENTATION-HISTORY.md#bounded-first-comparison-proposed--not-run)
is preserved as research, not the current product build order or permission to run.
