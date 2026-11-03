# Maintainer guide

[Getting started](../README.md) · [Optional workflows](usage.md)

## Current UX checks

On 2026-11-03, five fresh-context skill smoke checks and one follow-up used raw
source packets adapted from the [authored durability examples](../tests/fixtures/impact-first.json).
Workers received the skill and request, without prior findings or expected answers.
These were source-only checks; proposed regression tests were not executed.

| Request and setup | Observed response |
| --- | --- |
| Check my changes; staged-only ordering change | Found the acknowledgement-before-sync gap and named the staged scope. |
| Check my changes; clean feature branch tracking itself | Used the merge base with local main and found the gap. |
| Check my changes; clean main | Asked one scope question instead of auditing everything or returning a clean verdict. |
| Check durability; no Git metadata, unclear callback contract | Reviewed the explicit behavior and kept assertions conditional. |
| Review this repository; no Git metadata, protected implementation | Recognized the existing recovery assertion and returned no actionable finding. |
| Show me the proposed test; same conversation | Returned an unexecuted test sketch for the selected finding. |

All five source-packet inventories and hashes were unchanged after review. The
execution-fence bytes and prior research are unchanged. Packaging, standalone
copying (including the picker metadata), moved links, and instruction checks pass.
These small authored smoke checks are not a real-user usability study, a detection
benchmark, proof of model compliance, or evidence of advantage over ordinary review.
The real installer and picker activation still need their supported host; this
development environment has no Node.js/npx. CI checks real CLI delivery.

## Evidence and limitations

Copy/discovery was checked on 2026-10-18 with Codex CLI 0.163.0 on macOS 27.0.1
arm64. A [live six-case synthetic evaluation](../experiments/audit-evaluation/REPORT.md)
on 2026-10-19 used the actual skill through direct-file invocation: three intended
weaknesses found and no false positives on three protected controls, by manual
grading. Read-to-pre-response checkpoints took 9–21 seconds; these exclude final
response generation and startup. No setup was needed by the auditors. These small
authored cases do not establish effectiveness or speed on real repositories.

A [four-repository read-only pilot](../experiments/real-repository-pilot/REPORT.md)
completed on 2026-10-19: independent model review accepted 9 of 11 emitted findings
and left two unresolved; one of two predeclared historical gaps was found.
Measured full-response latency was 128–164 seconds, with no runtime setup.
Control-selection limitations and the missed gap limit reliability claims.
The [follow-up diagnosis](../experiments/audit-quality-diagnostics/REPORT.md) separates
visibility, contract and timing limits; improved future outcomes remain unmeasured.

A [four-cell packaging comparison](../experiments/packaging-2x2/REPORT.md) on
2026-10-20 crossed old/new instructions with absent/present historical specification
text. All four reports missed the targeted interaction; both specification-present
reports retained unsupported installed-mode assertions. That experiment did not
justify further instructions; one run per cell establishes no reliability or
speed gain.

## Maintainer notes

[RO-1: ordinary review versus Faultline](../experiments/ordinary-review-comparison/PROTOCOL.md)
is a prepared read-only comparison, **NOT FROZEN / NOT RUN**. Existing evaluations
do not establish incremental value over ordinary review; the current product
decision is **INCONCLUSIVE**. Six candidate scopes are prepared. The user serves
as both human curator and grader; grading is independent of audit workers, not
curation. Budget enforcement and the complete study freeze remain prerequisites.
This phase preserves issue #6's original executable study and dependencies.

A separately authorized [two-case pilot](../experiments/ordinary-review-comparison/PILOT-RESULTS.md)
completed four reviews on 2026-10-21 with provisional **NO CLEAR BENEFIT** over
ordinary review; case-level human grading remains pending. The current
**Critical Failure Challenge Loop** is a targeted, unmeasured revision: it makes
promise selection, consequence ranking, and repeatable recovery challenges
explicit while retaining source tracing and active refutation. The
[evaluation hypothesis and next comparison](../IMPLEMENTATION.md#3-check-that-audit-helps)
do not claim better detection, accuracy, clarity, speed, or cost. Historical
evaluation instructions and results are preserved unchanged.

[Design](../DESIGN.md) · [Implementation plan](../IMPLEMENTATION.md) ·
[Security research and unchanged execution gate](../ISOLATION.md) ·
[Historical design](../DESIGN-HISTORY.md) · [Historical plan](../IMPLEMENTATION-HISTORY.md)

Execution remains **NO_GO / UNAVAILABLE**. Qualification research and terminal
evidence are retained; custom VM runners, QEMU, Firecracker, and further Apple
Container qualification are deferred, not the default development direction.
Installing a skill or Docker, closing an issue, or declaring repository trust does
not lift the execution gate.

Focused maintainer checks (Python standard library only):

```sh
python3 -B -m unittest discover -s tests -p test_skill.py -v
python3 -B -m unittest discover -s tests -p test_install_delivery.py -v
python3 -B -m unittest discover -s tests -p test_spike_design.py -v
python3 -B -m unittest discover -s tests -p test_audit_evaluation.py -v
python3 -B -m unittest discover -s tests -p test_real_repository_evaluation.py -v
python3 -B -m unittest discover -s tests -p test_audit_diagnostics.py -v
python3 -B -m unittest discover -s tests -p test_counterexample_audit.py -v
python3 -B -m unittest discover -s tests -p test_impact_first.py -v
```

These inspect packaging, instruction boundaries, links, and frozen fixture
hashes/syntax and evaluation records. The six [impact-first examples](../tests/fixtures/impact-first.json)
specify weak and strong recovery protection, consequence ordering, unclear
contracts, artificial-error tests, and useful negative results. Their checks
validate authored examples and instructions, not observed model reasoning.
These checks do not execute target-project code, the frozen scenario, Docker,
or qualification procedures. Historical research has separate maintainer tests;
it is not part of the Audit workflow.
