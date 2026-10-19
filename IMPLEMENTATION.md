# Faultline implementation plan

**Current priority:** useful read-only Audit in minutes. Execution remains
**NO_GO / UNAVAILABLE**. Docker verification is a proposed later capability,
not an enabled mode or approval to change the existing authorization boundary.

## 1. Ship the Audit experience

Keep one canonical `faultline-audit/SKILL.md`. Change the skill, README, design,
implementation plan, and packaging/instruction checks together. No runtime,
dependency, service, CLI, additional skill, or sibling integration is needed.

- Accept a repository or paths; infer callers/tests and expected behavior.
- Read files as data without imports, discovery, tests, builds, scripts, Docker
  inspection, installs, or edits.
- Return up to three realistic, source-linked findings with the smallest useful
  test, confidence, uncertainty, and a distinction between suspected bugs and
  missing test protection. Say that tests were not run.
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
