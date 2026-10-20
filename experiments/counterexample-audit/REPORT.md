# Bounded counterexample step — 2026-10-20

The revised skill detected **3/3 frozen target contradictions versus 2/3 for
baseline**. Independent graders identified **zero unsupported claims, zero
false-positive claims and zero protected-control alarms in both arms**. Median
complete-response time was **117.504 s versus 135.881 s** (ratio 0.865). All
12 audits and 12 grades completed; there were no retries or failed sessions.
This meets the predeclared preliminary-signal rule on this small sample, not a
general detection, reliability or speed claim. Packaging contributes no result
to those denominators.

## Change and known-answer regression

The skill replaces one general tracing instruction with one internal, bounded
counterexample probe: establish the contract independently of test expectations;
trace concrete inputs through defaults, early exits and downstream exceptions;
compare supported modes; check whether tests bypass the path; require evidence
for a contradiction or offer conditional expectations. It adds no ordinary report
fields, runtime, dependency, setup requirement, or exhaustive input matrix.
Both execution fences and the existing report instructions are byte-identical.

The [packaging walkthrough](REGRESSIONS.md) explains why comparing two numbers
alone misses the default prerelease guard. Its answer is already known from
[upstream PR #794](https://github.com/pypa/packaging/pull/794/files), which adds
`<`/`>` to autodetection and changes the old False policy expectations. This is
a mechanism regression, **excluded from every held-out quality/speed denominator**.

The fresh [known-case report](known-regression/response.md) surfaced the blocked
comparator and forced-policy test bypass in 176.874 seconds. Its independent
[grade](known-grade/response.md) accepted that trace but kept the unconditional
default-True assertion unresolved: the supplied PEP packet did not include the
upstream policy correction, and the reviewer judged the comparison-to-policy
inference insufficient. It recorded three findings, five claims, one unsupported
claim, and no identified false-positive claim. That disputed grade is retained;
neither the known fix nor this fresh output demonstrates unbiased improvement.

## Frozen held-out comparison

An independent curator received no revised skill or prior Audit outputs. It
selected three public historical interaction bugs unused in prior Faultline
trials, plus their protected counterparts, rejecting a candidate whose immediate
fixed snapshot lacked exact interaction assertions. Each packet contains 9–10
complete, unmodified upstream files: production paths/callers, contract text,
tests and root test configuration. No issue summary, fix diff, injected hint or
oracle was given to auditors. Licenses, Git blob identities, acquisition metadata,
selection notes, and the predeclared per-case expectations are preserved in
[curation](curation/public-metadata.json).

| Family | Bug / protected packet | Frozen interaction |
| --- | --- | --- |
| urllib3 | c04 / c01 | Explicit Retry-After opt-out, cloning and status-retry sleep. |
| Flask | c02 / c05 | Silent JSON failure cached before a later non-silent call; an existing test bypasses the cache. |
| pytest | c06 / c03 | `--runxfail` bypasses normalization of ordinary skip-mark report locations. |

The [curator receipt](curation/freeze-receipt.json) precedes all audits. Both
instruction variants and [criteria](criteria.json) were frozen before receiving
case identities; the final [protocol](protocol.json) froze packets, prompts,
oracles, rubric, collector and schedule before the first audit. Baseline is the
exact PR #21 skill at `ec2effd2ed1a060482a967043672d90e4dc26278`. Revision is the
shipped skill; it was not retuned after any outcome.

There is one fresh ephemeral CLI session per packet/arm: 12 first responses, no
selective retries. Within each pair the source, literal request, path, requested
model (`gpt-6.1-sol`), effort (`xhigh`), CLI (`0.163.0`) and settings are identical.
Only skill bytes differ. Case order was seeded before outcomes; arm order
alternates, and two fixed workers each process whole pairs. Auditors receive one
staged packet and the skill, with history, other packets, answers, rubric, reports
and treatment labels withheld. Shared filesystem isolation relies on instructed
path limits and observed tool review, not an OS read barrier. Public historical
training familiarity cannot be excluded; "unused" does not mean novel to the model.

Fresh independent graders receive one report, its source packet, frozen per-case
oracle and rubric, with both skills and treatment labels withheld. They must
challenge the oracle, assess alternate findings, and preserve unsupported and
unresolved claims. A target contract question receives partial credit separately;
an unrelated valid gap does not erase a target miss. Controls certify only the
declared historical interaction. These are model source judgments, not human
adjudications or reproduced defects.

| Packet / role | Baseline primary result / seconds | Revised primary result / seconds |
| --- | --- | --- |
| c01 / protected | [protected; no alarm](audits/r04/response.md) / 157.240 | [protected; no alarm](audits/r03/response.md) / 114.037 |
| c02 / defective | [detected](audits/r08/response.md) / 117.170 | [detected](audits/r07/response.md) / 116.092 |
| c03 / protected | [protected; no alarm](audits/r09/response.md) / 160.883 | [protected; no alarm](audits/r10/response.md) / 118.917 |
| c04 / defective | [detected](audits/r12/response.md) / 97.323 | [detected](audits/r11/response.md) / 101.675 |
| c05 / protected | [protected; no alarm](audits/r01/response.md) / 143.309 | [protected; no alarm](audits/r02/response.md) / 120.833 |
| c06 / defective | [miss](audits/r05/response.md) / 128.453 | [detected](audits/r06/response.md) / 153.954 |

The additional detection is the pytest skip-location interaction: the revised
[report](audits/r06/response.md) and [grade](grades/g02/response.md) establish the
option/mark/reporting path; the baseline [report](audits/r05/response.md) and
[grade](grades/g03/response.md) retain a target miss despite two valid alternative
findings. Both skills detect the Flask and urllib3 targets. All six control
reports avoid alleging their protected historical defect; distinct valid gaps
remain admissible.

Baseline emitted 14 findings / 30 graded claims; revision emitted 15 / 31.
Graders accepted 29 baseline claims and kept one secondary debug-policy question
[unresolved but appropriately conditional](grades/g09/response.md); all 31 revised
claims were graded accepted. That does not settle the underlying debug contract
or establish superior ambiguity handling: independent single-report grading
and claim segmentation can differ. The [results](results.json), [grading mapping](grading-plan.json)
and raw grades preserve every claim, uncertainty and denominator. No grade was
rewritten or selectively retried.

## Timing, evidence and limits

The one-off [audit driver](run.py) and [grade driver](grade.py) reuse PR #21's
unchanged collector. Raw stdout/stderr, receive-time event ledgers, prompts,
packet hashes, final responses and timings are retained. Grading starts after
all audits, under a separately frozen blinded schedule. End-to-end timing runs
from just before process launch through the completion event, including startup,
queueing, generation and transport. It is not reasoning time or first-token time.

The speed guard was declared before outcomes: revised median at most 180 seconds
and at most 1.5× baseline. A positive preliminary signal additionally requires
more supported target contradictions with no increase in unsupported claims or
protected alarms. Ties do not establish improvement. Failures remain failures;
completed-only medians never stand in for missing quality outcomes.

The 482 captured commands across the 26 sessions use file readers/search
(`cat`, `nl`, `rg`, `sed`, plus `pwd`). [Tool review](tool-review.json) found no
observed target execution, history/network retrieval, audit oracle access, or
absolute file argument outside its permitted session packet. Captured reads do
not prove model attention or kernel isolation. Source/grade packets were unchanged
after every session. Preparation-only API payloads and curation scripts remain
local; [publication inventory](curation-publication.json) retains their frozen
identities. All audit/grade inputs, licensed raw source and source provenance
are archived unchanged.

Seventeen unique focused maintainer checks passed, including the three new
archive regressions; the existing PR #21 eight-session archive verifier also
passed. These run only maintainer checks on data, never target projects. The
standalone skill validator still fails with `ModuleNotFoundError: yaml`, including
a normal non-isolated invocation; no dependency was installed. Unrelated isolation
qualification tests/procedures were not rerun. The full-archive whitespace check
flags four trailing-space lines in unchanged upstream urllib3 documentation;
the authored-file whitespace check passes. Frozen input bytes were preserved.

The [focused checks](../../tests/test_counterexample_audit.py) verify frozen
identities, pair parity, complete-response endpoints and every graded claim's
accounting. They protect evidence integrity; they do not prove future model
compliance or semantic correctness. Bounded packets omit unrelated modules and
dependencies. Six packets, three bug families and one observation per arm cannot
establish reliability, a false-alarm rate, repeatability, causal attribution,
whole-repository speed or ordinary-user comprehension.

[Preservation](preservation.json) verifies all 103 original checkout files, Git
status and HEAD unchanged. Of 195 files in the PR #21 base, only the intended
canonical skill differs; all prior PR #20/#21 evidence, README, design, historical
plans, qualification material and execution fences are unchanged. This is a
separate focused branch stacked on unmerged PR #21, not a rewrite of either
evidence PR. Keep the new step provisional; repeated independent and human
review would be needed for broader quality claims.

No target code, imports, discovery, tests, builds, scripts, hooks, installation,
Docker, services or qualification ran. Source was read as data. The execution
gate remains **NO_GO / UNAVAILABLE**. No upstream notification or merge occurred.
