# Source-only regression cases

These known-answer cases come from PR #20. They are a manual regression rubric
and reference wording for the instruction clarification, **not new Audit runs**.
The coordinator reviewed the archived responses against this rubric. That review
is not blind or independent, and demonstrates no improvement in future detection.
Never import or execute the source or proposed tests. The canonical skill's
four finding fields and execution fence still apply.

## R1 — wrong-oracle conflict, with incomplete specification visibility

Input: the original [packaging scope](../real-repository-pilot/inputs/r1.txt) and
[unchanged snapshot](../real-repository-pilot/protocol.json). Withhold the oracle,
fix and this rubric from a future auditor.

Required regression check: trace the default `contains` path separately from the
shared test's forced `prereleases=True`. Notice that the exclusive-bound comparator
and autodetection policy differ, while the existing test expects `False`. Record
missing normative specification visibility. With only the original packet,
surfacing a contract conflict/question is acceptable; do not require an unsupported
claim of a reproduced bug or automatic specification retrieval. With the original
normative rule deliberately supplied in a later controlled evaluation, the expected
assertion is default membership of `3.0.0a7` in `<3.0.0a8`.

Archived outcome: the [report](../real-repository-pilot/audits/r1.md) omitted this
conflict and found two different gaps. The original historical miss remains a miss.
No new instruction specifically claims to fix it; visibility and reasoning have
not been separated experimentally.

## R2 — accepted API claim must not absorb an unsettled neighbor

Input: [Click finding 2](../real-repository-pilot/audits/r2.md), frozen source and
[claim-level grading](../real-repository-pilot/grades/r2.json).

Required regression check: keep `Context.lookup_default` and
`Parameter.get_default` expectations independent. The former's historical
compatibility evidence does not define the latter's raw missing-value contract.
An unconditional `get_default(...) is None` recommendation fails this check.

Reference correction: retain the supported direct `lookup_default` absence test.
Label the `Parameter.get_default` addendum a **contract question**: should its raw
missing result be `None` or an internal sentinel? If its public policy requires
`None`, assert `None` on that method directly. If sentinel exposure is intentional,
document and protect that policy separately. Neither outcome is established here.
This conditional reference is not a fourth confirmed finding.

Archived outcome: the first grader split F2a/F2b; the
[second reviewer](../real-repository-pilot/reviews/click.json) agreed F2b is
unresolved and conservatively kept the combined emitted finding unresolved.
The old 11-finding / 12-claim counts stay unchanged.

## R4 — a contract for initial preparation does not settle redirect policy

Input: [Requests finding 3](../real-repository-pilot/audits/r4.md), frozen
`prepare_request` / `rebuild_auth` source and [grade](../real-repository-pilot/grades/r4.json).

Required regression check: distinguish the observed credential replacement from
the desired policy. The mechanism is source-supported. The initial-request
precedence rule does not establish the competing-credentials redirect rule.
An unconditional assertion that account A survives is premature.

Reference correction: label a **contract question** about explicit account A versus
`.netrc` account B on a path-only redirect. If explicit credentials must persist,
mock B and assert the redirected copy retains A. If redirect reauthentication must
select B, document that exception and assert B instead. State which policy source
is missing. Do not present either assertion as an established regression oracle.

Archived outcome: medium-confidence suspected bug, with uncertainty stated but an
unconditional A assertion. The grader kept the claim unresolved. That grade stands.

## Automated checks and the next evaluation

The focused tests protect complete-response timing, overlapping event-span
accounting, original evidence bindings and byte-identical execution fences.
They do not grade free-form future model responses. No wording-match test is
presented as evidence of improved judgment.

A small controlled evaluation is worthwhile: four fresh packaging audits crossing
old/new skill with original packet / packet plus the frozen normative rule.
Freeze identical source, host/model/effort, ordinary request and independent grading;
withhold expectations and fix history. Predeclare one run per cell and retain every
outcome. Grade detection **or explicitly surfaced contract conflict** against the
information actually supplied. This is one known case, not a new reliability rate.
The two ambiguity cases above can be checked for conditional wording separately;
no new upstream contract has been established by changing instructions.

For that evaluation only, inventory relevant root test configuration and transitive
normative references as data; record each as supplied, absent or deliberately
withheld. Give auditors staged files only, without Git history access or lazy fetch.
Predeclare claim and whole-finding aggregation before grading. This adds no setup
requirement to ordinary Audit use. Keep model/effort fixed initially; a latency A/B
would need a separate change and matched repeated observations.

This PR does not start that evaluation or authorize target execution.
