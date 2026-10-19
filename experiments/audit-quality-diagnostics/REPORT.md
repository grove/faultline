# Audit-quality diagnosis after PR #20

This retrospective uses the [completed pilot](../real-repository-pilot/REPORT.md)
at `167131c1d0551ffa4c27b14b61974c14420db274`. No new audits, grading sessions or
target-project code were run. All original evidence, counts and limitations remain
unchanged. The instruction clarification below has **no measured detection or
speed improvement**.

## Historical miss: visibility limit and unreconciled evidence

Packaging's relevant source and assertions were in captured stdout by **21.280 s**,
before final text at 127.653 s:

| Evidence | Archived read | Consequence |
| --- | --- | --- |
| Default autodetection documentation | r1 `item_3`, 15.286 s | The default path depends on policy detection. |
| Guard omits `<` / `>` | r1 `item_7`, 21.280 s | Exclusive bounds do not enable prereleases automatically. |
| Shared test forces `prereleases=True` | r1 `item_6`, 21.279 s | Comparison assertions bypass default autodetection. |
| `<1.0.dev1` expects `False` | r1 `item_6`, 21.279 s | Existing assertions reinforce the historical policy error. |
| Comparator permits prerelease bounds; `contains` rejects first | r1 `item_7`, 21.280 s | A policy/comparison interaction needs reconciliation. |

[Visibility evidence](visibility.json) binds source lines, read IDs, timestamps and
output digests. Existing local stdout matched all **77 published audit-output
hashes and byte counts**. Captured presence does not prove model attention or
absence of host/model context truncation.

**Source-visibility failure:** normative external PEP 440 text was absent. Local
“inclusive operators” comments and `False` expectations made the intended policy
less clear than the preparer's oracle. Missing root test configuration limits
coverage judgments, but does not remove the visible interaction.

**Observed reasoning/output failure:** the [report](../real-repository-pilot/audits/r1.md)
never surfaced that interaction or conflicting policy evidence; it found two other
accepted gaps. This was not simply failure to open the files. Whether missing
specification, interpretation, attention or prioritization caused the omission is
unknown. No counterfactual or internal reasoning trace exists. The original miss
stands; no extra boundary rule is justified yet.

## Unresolved claims: contract ambiguity, with a separate grading effect

| Finding | Established | Unsettled | Small correction |
| --- | --- | --- | --- |
| Click F2 | Main `Context.lookup_default` claim accepted; neighboring `Parameter.get_default` also returns the sentinel. | Whether the latter raw API must return `None`; callers intentionally handle the sentinel. | Separate the API expectations; make the addendum a contract question with a conditional assertion. |
| Requests F3 | Redirect rebuilding can replace explicit account A with `.netrc` B. | Whether initial-request precedence persists during redirects; source also describes reapplication. | State the redirect-policy question; “retain A” is conditional. |

Both reports acknowledged uncertainty but supplied unconditional assertions.
Running tests would not decide these requirements. The skill now labels unsettled
expectations **contract questions**, makes their suggested assertions conditional,
and requires separate support for each API/lifecycle expectation. Neither contract
is resolved by this wording change.

**Grading effect:** Click F2 contains accepted F2a and unresolved F2b. The
[second reviewer](../real-repository-pilot/reviews/click.json) conservatively kept
the whole emitted finding unresolved. The original 11-finding / 12-claim accounting
stays intact. Separately, control assumptions for attrs F1 and Requests F1/F2 were
[disputed and accepted on second review](../real-repository-pilot/reviews/controls.json).
Those resolved disagreements are not the two unresolved claims. The original
control-selection limits and [grading errata](../real-repository-pilot/deviations.json)
remain attached.

## Latency: measured intervals, unresolved causal shares

The offline [calculator](analyze_latency.py) reads archived JSONL only:
`python3 -B experiments/audit-quality-diagnostics/analyze_latency.py`.
[Derived data](latency.json) retains input hashes and unrounded values.

| Case | Submission → turn start | Turn → last read received | Last read → full final text | Final text → completion | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| packaging | 1.362 s | 87.500 s | 38.791 s | 0.007 s | 127.660 s |
| Click | 0.799 s | 91.690 s | 43.989 s | 0.034 s | 136.513 s |
| attrs | 0.790 s | 82.546 s | 80.203 s | 0.042 s | 163.582 s |
| Requests | 0.698 s | 93.222 s | 45.593 s | 0.043 s | 139.556 s |

These mutually exclusive **event-receipt intervals** reconcile to the original
measurements. Pre-turn time combines launch and wait. Middle intervals combine
model/host processing, request waits, tool handling and buffering; they are not
measured “reasoning seconds.”

The union of command event-receipt spans is only **1.55–2.25 ms** per audit, with events
arriving almost together. Coalesced delivery cannot profile actual shell time or
assign the residual to model reasoning. The final message event contains the
**whole response**: its 7–43 ms gap to completion is not generation time.
First-token latency, UI rendering and execution-time telemetry are unavailable.

| Case | Read/search calls | Captured bytes, repeats included | Cumulative input / cached tokens | Output / reasoning tokens reported |
| --- | ---: | ---: | ---: | ---: |
| packaging | 17 | 266,433 | 351,492 / 261,248 | 5,389 / 2,869 |
| Click | 21 | 231,882 | 411,405 / 334,080 | 5,472 / 2,469 |
| attrs | 20 | 312,837 | 534,228 / 445,952 | 6,582 / 3,761 |
| Requests | 19 | 170,368 | 270,087 / 213,248 | 5,695 / 2,985 |

Byte counts refer to path-normalized archived stdout.
Broad overlapping reads, inference rounds and one exact repeated Click command
are observable workload. They plausibly contribute; their time shares are not
measured. The slowest case also has the largest byte/token totals, confounded by
task complexity. Input counts include repeated/cached context, not unique source;
output/reasoning counters are retained as reported, not summed as disjoint totals.

All sessions requested `xhigh` and overlapped on one host/account; grading briefly
overlapped the last audit. Effort, concurrency, queueing and transport costs
cannot be separated. No Docker, dependency installation or qualification ran.
The grading-only lazy fetch followed its Audit and cannot explain its latency.
Earlier tentative concerns appeared at **75.399, 39.388, 41.797 and 54.187 s**;
[bound excerpts](commentary.json) are not final actionable reports or first tokens.

## Changes, regressions and next step

Only the uncertainty instructions change. Advice-only and verification fences
retain their original bytes. [Three source-bound regression cases](REGRESSIONS.md)
cover the miss, mixed API claim and lifecycle transfer. Their reference corrections
are known-answer guidance, not fresh model outputs or blind validation.

Four new automated checks cover interval conservation, overlapping spans,
incomplete traces, evidence bindings and unchanged execution fences. The existing
ten focused checks also pass. The standalone validator still stops at missing
`yaml`; nothing was installed. Pilot evidence, qualification history, research and
original local work are preserved. Docker remains disabled, execution remains
**NO_GO / UNAVAILABLE**, and neither PR is merged.

A **four-run, one-case follow-up is worthwhile**: cross old/new skill with absent /
present frozen normative text, keeping everything else fixed. The
[regression rubric](REGRESSIONS.md) specifies visibility inventory, staged-file-only
grading and predeclared aggregation. These are evaluator preparations, not new
Audit setup requirements. One run per cell provides a preliminary signal, not
causal proof or a reliability estimate. No follow-up starts here.

Traceability and uncertainty guidance improve in this PR. Better discovery,
fewer unresolved outcomes, faster responses and human usability remain unproven.
Keep model settings and necessary counterevidence checks until a matched evaluation
can assess their tradeoffs.
