# RO-1 results and evidence record

**PLANNED — NOT FROZEN — NOT RUN (2026-10-20). Product decision: INCONCLUSIVE.**
This is a prepared template, not a completed study. No RO-1 audit, independent
grade, token charge or runtime observation is available. No additional model
experiments were dispatched. Earlier observations and their limits are linked
in [PROTOCOL.md](PROTOCOL.md); they are not paired ordinary-review evidence.

## Freeze and authority

| Field | Current value |
| --- | --- |
| Frozen bundle/commit, SHA-256 inventory and UTC freeze time | NOT FROZEN |
| Six candidate source cards and expected observations | PREPARED for human curation; see [fixtures.md](fixtures.md) |
| Exact upstream revisions and file hashes | [source-manifest.json](source-manifest.json): six projects, 57 files, 440,444 bytes; all extracted bytes matched pinned Git blobs |
| Human curator / grader | `grove` serves both, explicitly approved; independent of audit workers, not curation |
| Preparation agent / observer | Current assistant; cannot supply independent grades |
| Candidate agent/model configuration | Installed Codex CLI 0.163.0; propose the prior collector's requested `gpt-6.1-sol`, `xhigh`; no model dispatched or actual server identity observed |
| Effort, sampling, seed, context/output limits; unavailable settings | Candidate effort above; sampling/seed not set; complete launch configuration NOT FROZEN |
| Canonical skill | Base `f0e090c1e5e3e0e442c81778617e8eb2cd271430`, SHA-256 `5644276b8b8c94840bf02c2a7700d6fa7091e25002d8ad39e37d4d08aca77438` |
| Common request and arm instructions | Written in protocol; exact launch prompts NOT FROZEN |
| Case/arm/report order, access restrictions and observed tool evidence | NOT FROZEN |
| Timing/token/billing enforcement and rates; currency/date | UNAVAILABLE |
| Approval received | User: “Do it! I approve all of it”; sole-human curator/grader exception: “No, I am the sole human and must have both roles. I approve. Continue” (2026-10-20) |
| Exact frozen bundle approval | PENDING — actual cases/configuration are not frozen; approval to prepare is recorded above |

## All assigned slots

Keep these 12 slots even if the study stops early. A/B below identify arms for
readers; the grader initially receives randomized IDs. Do not convert unknowns
to zeros. NOT RUN means not attempted; UNAVAILABLE identifies a missing result
or prerequisite. Completed reviews may still have unresolved claims.

| Case | A status | B status | A/B report, tool/timing/usage evidence | Independent grade / B-only and A-only gaps |
| --- | --- | --- | --- | --- |
| c01 | NOT RUN | NOT RUN | UNAVAILABLE | UNAVAILABLE |
| c02 | NOT RUN | NOT RUN | UNAVAILABLE | UNAVAILABLE |
| c03 | NOT RUN | NOT RUN | UNAVAILABLE | UNAVAILABLE |
| c04 | NOT RUN | NOT RUN | UNAVAILABLE | UNAVAILABLE |
| c05 | NOT RUN | NOT RUN | UNAVAILABLE | UNAVAILABLE |
| c06 | NOT RUN | NOT RUN | UNAVAILABLE | UNAVAILABLE |

For each attempted slot, attach the following compact evidence note using existing
raw prompt/report/tool/timing artifacts where the host supplies them:

```text
Case / arm / blinded report ID / frozen packet identity:
First raw prompt and report locations + digests; full response captured?:
Observed tools/reads, source identity before/after, leakage/parity deviations:
Status: completed / timeout / failed / refused / skipped / unavailable / NOT RUN:
Stop/skip reason, retained partial output and unattempted work:
UTC submission/completion; full elapsed seconds; method/resolution/limitations:
Reported input/cached/output/reasoning tokens and counter semantics:
Actual monetary cost, rate source/date, or UNKNOWN and reason:
Human setup, first reading, source validation, comparison/clarification minutes:
Grader/date; source-only judgment; suspected unblinding and limitations:
```

Grade all claims, including unexpected findings and unsupported subclaims. Keep
initial judgments before revealing pairs; attach disagreements with the oracle.

| Case/report/claim | Behavior + proposed failure | Source/contract and test evidence (revision, path, lines) | Judgment + consequence | Proposed test: location/setup/action/assertion, alternatives/practicality | Confidence supported? | Paired overlap or distinct gap, with reason |
| --- | --- | --- | --- | --- | --- | --- |
| NO OBSERVATIONS | — | — | UNAVAILABLE | PROPOSED — NOT RUN | UNKNOWN | UNAVAILABLE |

## Summary after grading

Fill counts only from retained evidence. Currently completed audits: 0/12;
fully assessable pairs: 0/6. All other quality and cost measurements are
UNAVAILABLE, not zero findings, zero expense or evidence of a successful negative.

- B-only and A-only consequential actionable gaps, deduplicated with per-claim
  links; distinct cases/projects; net gain. Missing A reports cannot be B-only wins.
- Accepted/false-positive/unresolved/duplicate/out-of-scope claim counts against
  every emitted claim in each arm. Show false positives among adjudicated
  accepted/false-positive claims too; an empty denominator is unavailable.
- Frozen gap targets detected/missed; protected-scope alarms; correct no-findings,
  valid alternatives and uncertainty handling against their respective assigned
  opportunities. Keep unavailable outcomes visible in those denominators.
- Practical test proposals and adoption blockers; unsupported-confidence claims
  (including unresolved requirements with unconditional assertions).
- Per-slot elapsed times and timeouts; completed-only median/range with completion
  denominators. Cumulative and paired token/cost totals, cached/reasoning semantics,
  human minutes by category, shared preparation and B-specific overhead.
- Extra complexity: installation/configuration steps, skill-reading tokens/time,
  clarification rounds, invalid suggestions needing repair, and human effort
  attributable to the skill. No infrastructure is added to improve this measure.
- All stops, failures, skips, unavailable evidence, deviations and suspected
  leakage; any observed prohibited action. Observed tool records are not proof of
  kernel isolation or target behavior.

## Present decision and next action

**INCONCLUSIVE:** prior studies lack a matched ordinary-review arm; this study
has six prepared candidates but no frozen launch, human grades or qualified budget
enforcement. There is no demonstrated repeated incremental benefit to justify regular
Foundryline adoption, and insufficient comparative evidence to recommend STOP
or claim the current skill should be simplified. Keep product guidance unchanged.

Next: identify an existing host with established budget enforcement, then finish
the exact freeze for the sole human curator/grader. User approval of preparation,
the proposed ceilings and combined human roles is recorded above; this is not
a request to repeat it. Approval of a later concrete freeze remains distinct.
Until dispatch prerequisites are established, all
12 slots remain NOT RUN. Afterward apply the protocol's frozen decision rules,
not a retrospective success threshold. The executable #6 study remains separately
conditional on its original dependencies; no issue has been edited or closed.

## Preparation checks actually performed

Prepared against Faultline base `f0e090c1e5e3e0e442c81778617e8eb2cd271430` on
2026-10-20, using local documentation/archived evaluations and GitHub issue
#2/#4/#5/#6 inspection. No new A/B audits or independent grading occurred.

The existing standard-library maintainer checks passed: `test_skill.py` (5),
`test_audit_evaluation.py` (2), and `test_real_repository_evaluation.py` (3), each
via `python3 -B -m unittest discover -s tests -p <filename> -v`. These inspect
packaging and archived data; they do not run target-project code. A separate
read-only check verified 35 local links across the six authored Markdown files,
whitespace and budget arithmetic. These are preparation checks, not model
compliance or effectiveness evidence. Preparation elapsed time, model tokens,
monetary cost and human review effort were not instrumented and remain UNKNOWN.
Skill bytes, prior fixtures/results and safety qualification material were not
changed. No runner, dependency, schema, AI reviewer or product feature was added.

The user's subsequent approval assigns both human roles to `grove`. This overrides
the draft's separate-human requirement. Curator/grader independence is therefore
unavailable; worker-independent human judgment remains possible but pending.

After candidate preparation, the same ten maintainer checks passed again. A
source-only integrity check verified every one of the 57 extracted files against
its exact upstream Git blob, manifest identity and 440,444-byte total. The six
authored Markdown files then passed 39 local-link, whitespace and budget-arithmetic
checks. No fixture was imported or executed.

## Dispatch preflight actually performed

`codex --version` reported `codex-cli 0.163.0`; `codex exec --help` was read
without a model prompt. No authentication material was retrieved or printed.
The installed CLI's help showed sandbox, ephemeral and JSON-output options but
did not establish cumulative input/output, read-call or monetary limit enforcement.
This is not a claim that no Codex configuration could ever provide those controls.

Read-only inspection of the existing `experiments/packaging-2x2/run.py` collector
found timeout handling and final-event capture, but no cumulative token/tool or
cost stop. Its SHA-256 is
`8bbfb53abaaf719171fe105539908269331af668777576e9b8de6d45d6ed43c0`.
The counterexample driver reuses it; neither driver was executed or edited.

The current [official Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
describes experimental rollout-budget tracking/reminders and token weights.
That documentation does not establish hard enforcement or worst-case overshoot
for installed 0.163.0 under this study's separate cumulative input/output ceilings.
No account-specific billing rate or enforceable USD reservation was established.
Do not treat context-window or output-truncation settings as cumulative study caps.

**Preflight disposition: UNAVAILABLE; zero audit dispatches.** The user has
approved proceeding; the missing prerequisite is a demonstrated existing way to
bound token/tool usage and spending for the frozen run configuration, not another
general permission request. Do not add a runner/controller, install tools, inspect
credentials or spend model calls merely to qualify that prerequisite. All 12 run
slots remain NOT RUN; all human grades and incremental-benefit measurements remain
UNAVAILABLE. None of the prepared case hypotheses is counted as an audit finding.
