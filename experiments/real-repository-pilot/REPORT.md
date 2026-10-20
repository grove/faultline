# Four-repository read-only Audit pilot — 2026-10-19

The actual canonical Faultline skill completed **4/4 scoped audits**. Independent
model reviewers accepted **9/11 emitted findings**, left **2/11 unresolved**, and
identified **0/11 false positives**, duplicates or out-of-scope findings. Audit
found **1/2 predeclared historical gaps** and missed the packaging boundary gap.
These are source-review judgments, not reproduced bugs or a statistical estimate.

Measured submission-to-complete-response latency was **127.660–163.582 seconds**,
median **138.034 seconds**, including startup and final text generation. No audit
needed installation, Docker, execution approval, or operator clarification.
The skill remains unchanged. This supports a broader **advice-only trial with
reviewer judgment**; completeness and false-alarm reliability remain unestablished.

## Frozen cases and results

The [published plan](../real-repository-evaluation-plan.md) named these four
repositories. All scopes, snapshots, original bytes and private expectations were
[frozen](freeze.json) before the first audit. Two historical cases used the first
parent of an upstream fix; two controls used pinned repository HEADs with meaningful
existing assertions. No bugs were planted, cases replaced after results, or audits
retried. Auditors received only the skill, snapshot, selected behavior and ordinary
“find weak tests” request, with source-only safety restrictions.

| Case / frozen source | Predeclared expectation | Actual result, independently graded | End-to-end |
| --- | --- | --- | --- |
| r1 [packaging](https://github.com/pypa/packaging/tree/a716c52b5f3ca9b4a512f538b80ced8ee01b2775) | Exclusive prerelease-bound inclusion, before [#794](https://github.com/pypa/packaging/pull/794) | **Missed** `<3.0.0a8` admitting `3.0.0a7` by default. Two different accepted gaps: explicit object-level prerelease ban bypassed by filtering; arbitrary-equality autodetection exception. [Audit](audits/r1.md), [grade](grades/r1.json) | 127.660 s |
| r2 [Click](https://github.com/pallets/click/tree/fa7f035ab58dc4d9b8818b92fbc6a8f3c3234af6) | Missing public default lookup, before [#3224](https://github.com/pallets/click/pull/3224) | Found the expected `lookup_default` sentinel leak. Its finding also extends the concern to `Parameter.get_default`, whose missing-value contract remains unresolved. Two other accepted gaps: mapped defaults prompting despite docs; map-callable lazy evaluation. [Audit](audits/r2.md), [grade](grades/r2.json), [second review](reviews/click.json) | 136.513 s |
| r3 [attrs](https://github.com/python-attrs/attrs/tree/ee66e7274852438cc23d4240a1a9cd632fda8b52) | Converter-before-validator initialization order protected by exception and same-field assertions | Three accepted interaction gaps: later-field conversion before validation, earlier conversion before dependent factories, and validation failure before post-init side effects. Current implementation preserves these orders. [Audit](audits/r3.md), [grade](grades/r3.json), [dispute review](reviews/controls.json) | 163.582 s |
| r4 [Requests](https://github.com/psf/requests/tree/611c6162cbc4ac2020a2f91c7cfa4f3abf9bbb60) | Redirect host/scheme/port decisions protected; previous TLS walkthrough excluded | Two accepted gaps: cross-host upgrade branch precedence and isolated port changes. Competing explicit/`.netrc` credentials on same-origin redirects remains unresolved. [Audit](audits/r4.md), [grade](grades/r4.json), [dispute review](reviews/controls.json) | 139.556 s |

The packaging miss is retained as a future manual regression case. Existing
`False` expectations for exclusive prerelease bounds do not establish the intended
policy. The source's bound comparator and autodetection disagree; the upstream
[issue](https://github.com/pypa/packaging/issues/788) documents the specification
contract. External PEP 440 text was **not staged for the auditor**. Local source,
docstrings and docs were available, so this is a miss against the predeclared
oracle, with that information limitation attached.

The control preparation was too broad: existing assertions protect individual
behaviors but leave interaction boundaries open. Independent graders disputed
three protection assumptions (r3 F1; r4 F1/F2); a second fresh reviewer agreed with
the accepted gaps. Neither control received an identified false positive, but
these controls do **not** establish performance on exhaustively protected scopes.
Their unexpected valid gaps must not be presented as false alarms.

## Complete accounting and independent judgments

Four fresh graders neither prepared cases nor ran their audits. Two further fresh
reviews covered only disputed classifications. All are **LLM source judgments**,
not independent human grading. Original expectations, grades, disagreements and
responses are retained; the coordinator reconciled accounting and tool records.

| Exclusive class | Emitted findings (11) | Separately graded claims (12) |
| --- | ---: | ---: |
| Accepted gap | 9 | 10 |
| False positive | 0 | 0 |
| Duplicate | 0 | 0 |
| Out of scope | 0 | 0 |
| Unresolved | 2 | 2 |

Click finding 2 contains two API claims. Its main `Context.lookup_default` claim
is accepted and finds the historical gap; its `Parameter.get_default` addendum is
unresolved. The second reviewer conservatively classifies the **whole emitted
finding as unresolved**. Both claim-level grades remain visible. Nothing was
dropped to improve the score. False positives among adjudicated whole findings:
**0/(9 accepted + 0 false positives) = 0/9**, excluding two unresolved findings.
This conditional count is not a general false-positive rate or precision claim.

The other unresolved claim needs a redirect-specific authentication contract.
Neither unresolved claim is accepted as a confirmed bug or silently counted false.
Unknown new bugs have no recall denominator; the only miss count is **1/2 known
historical gaps**. See [results and adjudication](results.json).

## Clarity, actionability and ease of use

On a first read, graders located a test location, concrete setup/action, expected
assertion and supporting source for **11/11 findings**. They judged all explanations
clear; **two finding units need contract clarification** before adopting their full
recommendations. This is subjective model assessment, not measured developer
comprehension or proof that every proposed assertion is correct.

Receipt of each first-read field-location screen took **11.509, 10.806, 10.306 and
9.302 seconds** from grader submission, including startup. [Screens](screens) and
separate [grading timings](timings) are preserved. These are not two-minute human
usability results. Complete primary grading took 129.744–211.637 seconds per case;
the disputed reviews took 171.378 and 119.268 seconds, separately from Audit latency.

The direct skill-file prompt worked without runtime setup in all four sessions.
However, an expert selected the behaviors and staged relevant sources. This does
not measure novice scope selection, a whole-repository “find weak tests” request,
or skill discovery/installation. No operator clarification was requested.

## Timing, reproduction and retained evidence

The existing Codex CLI 0.163.0 ran four fresh ephemeral sessions on macOS 27.0.1
arm64, requesting the existing host model/effort (`gpt-6.1-sol`, `xhigh`). Actual
server model identity was not separately exposed. All used read-only sandboxing,
approval `never`, web disabled and user configuration ignored. Sessions overlapped
on the same host/account; these are observed concurrent latencies, not isolated
serial benchmarks. Grading briefly overlapped the last audit.

A one-off standard-library [observer transcript](observer.py.txt) started the
monotonic clock immediately before host launch/submission and stopped on receipt
of `turn.completed` **after the full final `agent_message`**. It includes startup,
queueing, source/skill reading, tools, reasoning and output generation. It is not a
pre-final timestamp or coordinator poll. Clock resolution is about 42 ns, not an
accuracy claim; stream buffering, scheduling and preceding event handling are included.
The terminal-line timestamp precedes its JSON parse; UTC end is sampled just after.
Summary times are rounded to 0.001 s. UI rendering and monetary cost are unmeasured.

Source acquisition used bare public Git clones with hooks disabled, then archived
regular source/test/docs files as data. No checkout, imports or project commands
ran. Initial staging measured 3.948 s; final staging measured 0.846 s. Clone,
selection and total preparation time were not fully instrumented and remain
**UNKNOWN**. These evaluation costs are separate from Audit response time.

To repeat manually, acquire the exact [source identities and file hashes](source-manifest.json),
read files as data, and give a fresh existing coding agent the corresponding
[input](inputs) plus the canonical skill. Withhold expectations, reports and fix
history. Retain the first response and any stop; use a ten-minute ceiling. Future
responses may differ. No collector, second model or new dependency is a product
prerequisite. Never execute the source or proposed tests to repeat this pilot.

[Protocol](protocol.json), [frozen inputs](freeze.json), [expectations](expectations.json),
[raw anonymized audits](audits), [raw grades](grades), [second reviews](reviews),
[host event ledgers](events), [timings](timings), and [artifact hashes](artifact-manifest.json)
retain identities and outcomes. Local path prefixes/session IDs are normalized;
wording is otherwise unchanged. Published ledgers retain command/output identities
without vendoring upstream source. Original and normalized prompt digests are
separately labeled. Answer isolation relied on instructions and observed reads,
not an OS barrier between shared files.

A grading-only Git read attempted an implicit partial-clone download; the sandbox
blocked DNS/network access. Lazy fetching was then disabled in the task-local
clones. The four auditors made no observed network calls. A different grader's
raw limitation paragraph incorrectly attributed such an attempt to its own case;
the command ledger contradicts that attribution, so it is corrected in
[deviations and grading errata](deviations.json), with the raw grade preserved.
No target execution occurred. This is tool-event inspection, not kernel telemetry
or a sandbox qualification result.

## Comparison, decision and validation

[PR #19's synthetic evaluation](../audit-evaluation/REPORT.md) found 3/3 authored
weaknesses and no false positives on three controls, graded by its fixture author.
This pilot found 1/2 predeclared historical gaps plus other useful gaps, with
independent model grading, two unresolved findings and imperfect control selection.
The samples, contracts and grading differ; no superiority or statistical confidence
comparison is justified. PR #19's 9–21 s checkpoints excluded startup and final
generation, so **they cannot be compared numerically with this pilot's end-to-end
latency**.

Keep the canonical skill unchanged: the observed miss is real, but this run does
not isolate an instruction defect or demonstrate that an added rule would fix it.
The skill already requires boundary tracing, contract evidence, counterevidence
and uncertainty. Retain the miss for a future targeted regression audit when a
specific correction is proposed; no best-of retry was performed here.

The Audit-first experience produced concrete test suggestions within three minutes
on these selected scopes. Broader advice-only use is reasonable with developer
review. Reliable completeness, robust false-positive calibration, human usability,
repeatability, multi-language behavior and superiority to ordinary review remain
open. Public historical bugs may also be familiar from model training.

Ten focused maintainer checks pass: the existing seven plus three pilot evidence,
completion-timing and denominator checks. They verify archived records, not future
model behavior, upstream bug reproduction, or target tests. The standalone skill
validator still fails before validation because `yaml` is missing; nothing was
installed. All 254 staged files retain their original bytes. Preservation checks
retain the original local work, execution gate, qualification evidence, historical
plans and earlier experiments. **Docker remains disabled; execution remains
NO_GO / UNAVAILABLE.** This pilot enables no execution permission or merge.
