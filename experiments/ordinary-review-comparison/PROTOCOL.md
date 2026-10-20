# RO-1: ordinary review versus Faultline

**DRAFT — NOT FROZEN — NOT RUN (2026-10-20). Decision: INCONCLUSIVE.**
This is a proposed six-case, source-only comparison of the shipped Audit skill
with ordinary AI-assisted code and test review. It measures additional useful
test weaknesses, not implementation delivery, mutation strength or correctness.
No model experiments are authorized by this document.

## Scope and existing evidence

[Issue #6](https://github.com/grove/faultline/issues/6) specifies an executable
three-arm study, dependent on [#4](https://github.com/grove/faultline/issues/4)
and [#5](https://github.com/grove/faultline/issues/5), including the safety gate
in [#2](https://github.com/grove/faultline/issues/2). RO-1 is a separately
identifiable proposal; it neither satisfies nor removes those dependencies.
The original study remains conditional future work with its original acceptance
criteria and separate execution authorization. **NO_GO / UNAVAILABLE** remains.

Existing observations are retained, not new RO-1 results:

| Evidence | Actual observation | Limit for this decision |
| --- | --- | --- |
| [Walkthrough](../audit-walkthrough.md) | Two known historical examples and desk checks | Answers visible; no blind discovery or ordinary-review arm |
| [Synthetic evaluation](../audit-evaluation/REPORT.md) | Three intended weaknesses found; no alarms on three controls | Fixture author graded; tiny explicit-contract cases; timing excludes full responses; no ordinary-review arm |
| [Real-repository pilot](../real-repository-pilot/REPORT.md) | Model graders accepted 9/11 findings; two unresolved; 1/2 historical targets found | Imperfect protected controls, missing normative text, no human grading or ordinary-review arm; full preparation/monetary costs unknown |
| [Diagnostics](../audit-quality-diagnostics/REPORT.md) | Archived reads expose visibility and contract limits | Retrospective; instruction clarification has no measured benefit |
| [Packaging 2×2](../packaging-2x2/REPORT.md) | All four missed the target; two reports retained unsupported assertions | One rehearsed case; compares instructions/visibility, not ordinary review; model-only grading |
| [Counterexample comparison](../counterexample-audit/REPORT.md) | Revised skill found 3/3 targets versus old skill's 2/3; no graded protected alarms | Both arms used Faultline; only three bug families; single observations and model judgments, not incremental value over ordinary review |

These archives establish neither repeated incremental benefit nor absence of it.
Do not repurpose their cases as fresh holdouts or their graders as independent
human validation. No skill change or Foundryline integration follows from RO-1
preparation.

## Select six cases before seeing outputs

The user is the sole human curator and grader, as explicitly approved on
2026-10-20. This preparation agent may shortlist and document cases but does not
conduct the audit arms or supply independent grades. The user approves the final
case selection and later grades the first reports. Grading is independent of the
audit workers, **not independent of curation**; disclose the resulting confirmation
bias risk and do not describe this as fully independent human validation.
Select six small public Python scopes from at least four projects and six distinct
behaviors. Use unmodified
source/tests/docs at immutable revisions. Do not pair a bug with its fixed twin
or count multiple variants of one behavior as independent cases.

Reserve two consequential protection gaps (prefer one current bug and one correct
implementation with weak tests), two adequately protected scopes (one low-risk),
one contract-consistent alternative implementation, and one genuinely ambiguous
contract. A control protects only its declared behavior, not an entire repository.
The ambiguity case needs conflicting or absent authority, not a hidden known answer.
Six prepared candidates, their expected observations and rejection criteria are
in [fixtures.md](fixtures.md); exact revisions/files are in
[source-manifest.json](source-manifest.json). They await human curation and are
not results. The study is not frozen while dispatch limits are unqualified.

Define a candidate pool and order before detailed inspection. Record every
candidate, including exclusions and their reasons, then take the first eligible
case in each category. Eligibility requires a real consequence, a bounded review
scope, and enough caller/helper/configuration/contract context for both arms to
judge it. Selection must not depend on a Faultline report, an instruction-specific
failure pattern, or a pilot run. If the mix cannot be obtained within preparation
limits, stop; do not substitute convenient rehearsed cases.

Exclude all cases/behaviors in this repository's previous experiments, including
delivery thresholds, discount-state rejection, retry deduplication, URL leading
spaces, Requests TLS/redirect credentials, packaging prereleases, Click defaults,
attrs initialization order, urllib3 Retry-After, Flask JSON cache and pytest
skip-location handling. Record other known exposure. Public historical sources
may be in training data; absence of training leakage cannot be certified. Prefer
unrehearsed maintainer-selected scopes over famous fixes. Do not plant mutations
or author fixtures to demonstrate the skill's wording.

## Freeze and approve once, before the first audit

Use existing source-manifest, expectations, prompt, raw-report and timing practices
as examples; plain case cards and tables suffice. No new schema or runner.
Store withheld expectations separately from the agent-accessible source packets.
The curator freezes a dated immutable commit or hashed bundle containing:

- All six case identities, upstream commit IDs, complete file inventory and
  SHA-256 values, source acquisition/provenance and licenses, selected behavior,
  packet omissions and transitive references. Only regular source data; no
  checkout hooks, executable acquisition helpers, submodules or escaping links.
- Withheld source-grounded expected observations, precise contract citations,
  plausible consequential failures that assertions miss, protected assertions,
  acceptable alternatives and ambiguity/refutation evidence. These are hypotheses
  for grading, not observed runtime results. Freeze rejection notes too.
- Exact common request and arm instructions below, canonical
  `faultline-audit/SKILL.md` commit and SHA-256, host/agent versions, requested
  model/version, reasoning level, sampling/seed settings where supported, context
  and output limits, tool restrictions, telemetry and billing method. Record
  unavailable server identity/settings explicitly; no silent model fallback.
- Human curator/grader: GitHub user `grove`, serving both roles at their explicit
  request. Keep audit workers separate from curation/grading. Freeze the rubric
  below, anonymized report order,
  case order, arm order, cost limits and decision thresholds.
- Exact authorized source/output locations, preparation effort spent, and user
  approval referencing that bundle and the finite spending ceiling.

Use six fresh contexts per arm, no retained memory, other skills or earlier
reports. Same agent/model configuration, source packet and tool access in each
pair; only B receives the canonical skill. A must not auto-discover Faultline
through repository/global skills or inherited instructions. Log unavoidable host
instructions; if they introduce Faultline guidance into A, do not launch.
Keep answers, history, fix diffs, grading material and the experiment checkout
outside permitted reads for both arms. Record whether access limits are enforced
or instructed; inspect observed reads and stop on leakage. This is not sandbox
qualification. No network or history retrieval by either auditor.

Shuffle case order once and record it before outputs. Alternate which arm runs
first across pairs; run serially on the same host/account to reduce contention.
No feedback, hints, retries, skill tuning or case replacement after freeze.

## Matched review request and finite budget

Common request, replacing only the frozen scope path in both arms:

```text
Review the source and tests in <scope> for consequential missing assertions,
negative cases and test weaknesses. Suggest practical regression tests for useful
findings. No findings or uncertainty are valid outcomes. Read files as data only;
do not execute project code or change files. Return your review in conversation.
```

A receives that request using the ordinary coding agent. B additionally receives:
`Use the supplied canonical faultline-audit/SKILL.md for this review.`
Do not paste a specially improved Faultline prompt into B or require A to follow
Faultline's format/reasoning. Both receive identical read-only safety/tool limits.
Both may use host file readers/search (`cat`, `rg`, `sed`, `nl`, `ls`, `pwd`) within
their frozen packet and B may read the skill. No repository helpers, imports,
discovery, tests, builds, scripts, installs, fault injection, mutation engines,
Docker, VMs, service probes, target writes or upstream publication.

Proposed ceilings, subject to explicit approval of the completed freeze:

| Resource | Per audit | Whole study maximum |
| --- | --- | --- |
| First responses | One | 12; no extra AI curator/grader/reviewer calls |
| Submission through full response/timeout | 6 minutes | 72 minutes of audit time |
| Cumulative reported input, including repeated/cached context and instructions | 120,000 tokens | 1,440,000 tokens |
| Reported output, including reasoning where metered | 6,000 tokens | 72,000 tokens |
| Read/search calls | 25 | 300 |
| Model expenditure, using actual applicable billing | No pair gets extra funds | USD 30 total |
| Human preparation / grading and comparison | Shared preparation recorded separately | 90 / 90 minutes; 180 minutes total |

Whichever limit is reached first wins. Skill reading uses B's budget. Reserve
enough of the spending cap for a whole pair before starting it; stop when that
cannot be established. Existing host limit/counter facilities must bound use
without a new runner. If token/cost limits cannot be enforced or conservatively
bounded using the frozen billing method, the study is UNAVAILABLE; do not dispatch.
Missing post-run telemetry is UNKNOWN, never zero, and prevents a cost-qualified
KEEP. Record cache and reasoning counters as reported without double counting.
Do not install anything or launch existing evaluation drivers to repair this.

An observer times actual submission through receipt of the complete final response
using host events or a declared stopwatch method. Preserve raw prompts, outputs,
tool records, limit/stop events, UTC endpoints and elapsed intervals. No pre-final
checkpoint substitutes for response completion. Record human preparation, report
reading, source validation, comparison and clarification time separately. Shared
acquisition is not counted twice; B-specific setup/skill maintenance is extra cost.

## Independent source-only grading

The sole human curator/grader (`grove`), who does not conduct the audit arms,
grades all first reports against the frozen sources and expectations. Supply
random report IDs, with arm labels,
skills and counterpart outputs withheld during initial grading. Wording can reveal
the treatment; record suspected unblinding. No additional AI reviewer. Preserve
first judgments, disagreements with the oracle and later comparison separately.
If the worker-independent human has not graded a report, its grade remains
UNAVAILABLE; the preparation assistant cannot fill it in.

Split materially distinct claims, then deduplicate by behavior, reachable scenario
and missing observable assertion, not wording. Grade every claim, including new
ones absent from the oracle: accepted consequential gap, false positive, unresolved,
duplicate or out of scope. Cite exact source/test locations for each judgment.
False positives include unreachable paths, already-protected behavior and rejection
of a contract-consistent alternative. Missing authority is unresolved; confident
assertions without authority are also recorded as unsupported confidence. Keep
mixed findings' unsupported subclaims visible rather than accepting the whole unit.

An accepted consequential gap needs a reachable input/state, a practical user
impact (wrong result, lost/duplicated state, compatibility or trust-boundary
failure), authority for the expectation, and a traced reason the selected tests,
helpers and fixtures miss that observation. More assertions or stylistic coverage
alone earn no credit. A correct implementation may have a real protection gap;
that does not establish an implementation bug. Human source validation is not
test execution or proof that the tests pass or miss the scenario at runtime.

Grade test proposals separately: identifiable existing test location/hook,
concrete setup/action, observable assertion with contract support, would distinguish
the hypothesized failure by inspection, accepts valid alternatives, and practical
without a new framework or excessive mocking. Mark each yes/no/unresolved and
record adoption blockers and human assessment time. Tests remain PROPOSED — NOT RUN.
Correct uncertainty requires identifying the unresolved policy and a conditional
test/clarification; a generic caveat does not excuse an unconditional assertion.
Correct no-finding requires source-supported protection or a justified low-risk
scope; silence on a frozen gap is a miss, not a correct negative.

After grading, reveal pairs. Count B-only accepted actionable consequential gaps
that A did not describe, and A-only gaps symmetrically. A different proposed test
for the same weakness is not incremental discovery. Never count an A timeout,
missing report or unresolved grade as a B-only win. Report paired comparisons
only for fully assessable pairs alongside all 12 assigned slots. List target
misses against frozen gap cases only; unknown new gaps have no recall denominator.
Report every claim category/total, unsupported confidence, protected-scope alarms,
correct negatives/uncertainty and practical test proposals. Use [RESULTS.md](RESULTS.md).

## Stops and product decision

Stop immediately for unauthorized effects/attempts, source drift, answer leakage,
model/configuration mismatch, missing independent grading or any budget boundary.
Retain partial outputs, actual spend and reason; label attempted incomplete runs
as such and all remaining slots NOT RUN. Never replace a failed pair or silently
extend its allowance. Ambiguous cases may be completed reviews with inconclusive
claims. A deliberate low-risk no-finding is a completed review; an unattempted
case is NOT RUN, and a missing prerequisite is UNAVAILABLE.

There is no outcome-based early success stop. After the fixed sample or a required
stop, apply these predeclared rules in order:

1. **INCONCLUSIVE:** safety/leakage/parity failure, incomplete pairs, missing
   independent judgments/cost data, or fewer than two assessable consequential-gap
   opportunities. Unknown outcomes cannot establish no benefit.
2. **KEEP:** at least two B-only practical, independently accepted consequential
   gaps on two distinct cases/projects, more B-only than A-only gaps, no increase
   in false positives or unsupported-confidence claims, and correct handling of
   both protected controls, the alternative and ambiguity case. B's median audit
   elapsed time and total human review minutes must each be at most 1.5× A's,
   within all absolute limits. A zero-time denominator yields unavailable, not
   an infinite allowance. This supports only provisional optional use; fresh
   holdouts are required before regular Foundryline adoption.
3. **SIMPLIFY:** some validated incremental benefit exists, but KEEP's repetition,
   cost or noise threshold fails. Retain only guidance supported by the paired
   evidence; propose a deletion/narrowing, not a new feature or automatic edit.
4. **STOP:** complete, adequately judged pairs demonstrate no B-only consequential
   actionable gap. Stop expanding the skill/integration on this evidence; retain
   ordinary review and the archive. This is no demonstrated benefit at this budget,
   not proof Faultline can never help.

## Proposed tracking for #6

Recommend a separate linked issue titled **RO-1: compare existing read-only Audit
with ordinary review**, referencing this protocol and its eventual frozen bundle.
Its acceptance is freeze/approval, all assigned outcomes and costs, independent
human grading, and a product decision. Do not give it execution dependencies: it
does not execute or satisfy them. Add a labeled pointer in #6 only after authorized
tracker editing, explicitly retaining #6's original #4/#5/#2 chain and three-arm
criteria as conditional future work. Do not mark #6 done from RO-1 or close #2,
#4 or #5. This proposal makes no tracker changes.

The six candidate cards and source identities are now prepared. The user's
approval to continue and serve both human roles is recorded in
[RESULTS.md](RESULTS.md). Model dispatch remains UNAVAILABLE because the existing
collector has no established enforcement for this study's cumulative token/tool
and USD ceilings, and account-specific billing is unknown. Do not build a new
controller to compensate. Once an existing bounded host is identified, finish
the exact freeze for human curation/approval before any audit. Publication of
this preparation does not authorize target execution or complete #6.
