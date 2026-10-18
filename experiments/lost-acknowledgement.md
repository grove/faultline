# Lost acknowledgement / same-key retry — frozen design v1

**Issue:** [#10](https://github.com/grove/faultline/issues/10).
**Decision, 2026-10-18: NARROW. Execution: UNAVAILABLE / NOT RUN.**
This is the permitted design deliverable, not an executed spike or an enabled
skill. The [#2 host receipt](../qualification/2026-10-18-macos.json) records twelve
failed native launches and zero child starts. It establishes no isolation for
these fixtures. Do not extract/import/run the code below on this host. No live
qualification, fixture process, worker assessment, or comparison was attempted.

## Contract and cheaper alternative

Contract authority is the authored fixture requirement in
[#10](https://github.com/grove/faultline/issues/10), frozen here for these synthetic
controls only: **one logical order key causes at most one ledger effect, including
a retry after an acknowledgement is lost**. It is not a claim about any existing
payment product. A successful first request records exactly one `(key, amount)`
entry and returns a receipt. The selected input is `("order-17", 1250)` twice,
in minor units; no real money or external service exists.

Scope is sequential requests in one process using the same service and ledger.
The transport loses exactly the first acknowledgement, after the service has
committed the effect and returned to the transport, before the caller receives
success. The caller catches only that transport exception and retries once with
the identical key and amount. No concurrency, sleeps, restart durability, changed
payload for the same key, other keys, or second state-transition case is assessed.

**Cheaper-first decision: DIRECT TEST REVIEW / SKIP additional experiment for this
known pair.** Read the two `apply` methods: one remembers receipts, the other
always records again. The smallest regression is two same-key calls followed by
`ledger.effects == [("order-17", 1250)]`. This already distinguishes the seeded
defect without simulating lost acknowledgements. The hook below is a future
mechanics check, not evidence that C improves on negative-case review B. This
inspection is not an observed execution or an independent comparative trial.

## Frozen sources (data, not executable files)

Each named fenced block specifies the exact UTF-8 bytes of one proposed file,
with LF newlines and one final newline. The manifest below freezes their SHA-256
identities. Retain this document's Git commit and manifest before any future run;
a changed block/contract/oracle is a new revision, never a rerun of v1. Maintainer
checks parse syntax and hash text only; they must not execute these blocks.

The authored implementations are separate original candidates, not a mutation
performed during a challenge. Each receives the same trusted fake ledger.
`record` is the sole effect boundary; the transport hook is outside both candidates.

### Correct control: `deduplicating.py`

<!-- file: deduplicating.py -->
```python
class Service:
    def __init__(self, ledger):
        self.ledger = ledger
        self.receipts = {}

    def apply(self, key, amount):
        if key not in self.receipts:
            self.receipts[key] = self.ledger.record(key, amount)
        return self.receipts[key]
```

### Deliberately defective control: `reapplying.py`

<!-- file: reapplying.py -->
```python
class Service:
    def __init__(self, ledger):
        self.ledger = ledger

    def apply(self, key, amount):
        return self.ledger.record(key, amount)
```

### Common fake, caller, and deterministic hook: `scenario.py`

This fixed driver emits measurements, not a correctness verdict. Its process exit
status alone cannot establish a violation. Keep it immutable alongside the
candidates; do not let an assessed worker replace the ledger or edit the oracle.

<!-- file: scenario.py -->
```python
import json
import runpy
import sys


class LostAcknowledgement(Exception):
    pass


class Ledger:
    def __init__(self, events):
        self.effects = []
        self.events = events

    def record(self, key, amount):
        self.effects.append((key, amount))
        receipt = "receipt-" + str(len(self.effects))
        self.events.append(["effect", key, amount, receipt])
        return receipt


def scenario(candidate, mode):
    if mode not in ("baseline", "lost-ack"):
        raise ValueError("unknown scenario")
    events = []
    ledger = Ledger(events)
    service = runpy.run_path(candidate)["Service"](ledger)
    responses = []
    losses = 0
    attempts = 0

    def send():
        nonlocal losses, attempts
        attempts += 1
        events.append(["request", "order-17", 1250])
        receipt = service.apply("order-17", 1250)
        if mode == "lost-ack" and attempts == 1:
            losses += 1
            events.append(["ack-lost", receipt])
            raise LostAcknowledgement()
        events.append(["ack", receipt])
        responses.append(receipt)

    try:
        send()
    except LostAcknowledgement:
        events.append(["retry", "order-17", 1250])
        send()
    return {"mode": mode, "attempts": attempts, "losses": losses,
            "effects": ledger.effects, "responses": responses, "events": events}


if __name__ == "__main__":
    candidate, mode = sys.argv[1:]
    print(json.dumps(scenario(candidate, mode)))
```

### SHA-256 manifest

| Proposed file | SHA-256 of fenced bytes |
| --- | --- |
| `deduplicating.py` | `1b598455883ec558ab40d2df9e25b9c4eee038d8d964c1c6a87848320fc23e3f` |
| `reapplying.py` | `86d826fc3e59a16ba8fc912664b9788d19fc8b1c040aafb09c8c92f6580489f7` |
| `scenario.py` | `560a0bf8bdb8b9bc4f0e976d931c355798d9c5a124feef2c93e302e050b1d659` |

## Oracle and contrary outcomes — expectations only, NOT RUN

The contract supplies the oracle independently of either candidate's return
value: count the trusted ledger's actual effects for `order-17`, and inspect
the ordered hook/caller trace. A receipt string or exception alone is insufficient.
For these exact candidates, freeze all expectations before any worker run:

| Candidate / condition | Attempts / losses | Ledger effects (JSON form) | Caller responses | Expected interpretation if independently evidenced |
| --- | --- | --- | --- | --- |
| Either / baseline | 1 / 0 | `[["order-17", 1250]]` | `["receipt-1"]` | Passing unchanged control |
| Deduplicating / lost-ack | 2 / 1 | `[["order-17", 1250]]` | `["receipt-1"]` | NO_VIOLATION_OBSERVED in this scope |
| Reapplying / lost-ack | 2 / 1 | `[["order-17", 1250], ["order-17", 1250]]` | `["receipt-2"]` | VIOLATION_OBSERVED in this seeded fixture only |

Required baseline trace: `request, effect, ack`. Required injected trace for
deduplicating: `request, effect, ack-lost, retry, request, ack`; for reapplying:
`request, effect, ack-lost, retry, request, effect, ack`. Each request/retry must
carry the fixed key and amount. The first effect must precede the single lost
acknowledgement; no first response may reach the caller. Two effects under the
correct control, one under the defective control, or a missing/misplaced loss
contradicts this frozen mechanics expectation: investigate the hook, source drift,
and measurement first; do not relabel the expected answer as an observation.

For a different implementation, one effect with a contract-permitted explicit
retry rejection is also legitimate under the at-most-once invariant. A valid
serialization, rejection, or rollback must not be condemned for returning a
different receipt/status. Such a candidate needs its own predeclared driver and
normal-success contract; this fixed driver's uncaught exception cannot validate
that alternative. Zero effects does not violate at-most-once alone, but contradicts
this fixture's successful-first-request/reachable-post-commit setup and cannot
validate this challenge. Never invent a liveness or durability requirement.

An independent grader checks the original bytes, baseline, ledger, hook ordering,
and replay against this table. These public seeded expectations are **not a
withheld evaluation oracle**. The current author/agent knows both answers and
cannot be an independent, blinded assessor of these cases.

## Conditional execution plan — NOT RUN, no authorization

First obtain fresh actual-host qualification under [ISOLATION](../ISOLATION.md),
covering the fake, transport hook, retry/reset paths and descendant cleanup.
Then obtain caller authority for the exact host, installed Python executable and
version, immutable input paths, selected argv/cwd, disposable resources, permitted
output/retention and finite limits. Do not rerun the failed launcher outside this
agent's boundary or substitute an ordinary shell. No installations or network.

Only on that qualified, separately authorized host, the trusted preparer would
extract the three blocks verbatim, verify the manifest, and mount inputs read-only
as `/fixture`. The collector/oracle/retained originals remain outside the worker's
writable boundary. Use a new empty `/work` for each process, a host-approved
minimal environment and no credential handles. `/approved/python3` below is a
placeholder for the explicitly selected installed executable, not a working
command or sandbox launcher. Freeze the real executable identity and host launch
envelope before execution; do not infer either from these argv templates.

All commands have cwd `/work` and use the qualified host's launch envelope:

| Step | Proposed child argv (JSON array) |
| --- | --- |
| Correct baseline | `["/approved/python3", "-I", "-S", "-B", "/fixture/scenario.py", "/fixture/deduplicating.py", "baseline"]` |
| Defective baseline | `["/approved/python3", "-I", "-S", "-B", "/fixture/scenario.py", "/fixture/reapplying.py", "baseline"]` |
| Correct injection | `["/approved/python3", "-I", "-S", "-B", "/fixture/scenario.py", "/fixture/deduplicating.py", "lost-ack"]` |
| Defective injection | `["/approved/python3", "-I", "-S", "-B", "/fixture/scenario.py", "/fixture/reapplying.py", "lost-ack"]` |

Run both unchanged baselines before attribution. Each process constructs a fresh
service/ledger; neither candidate nor driver is patched between baseline and
injection. Replay both injected commands once, independently reset, to check
repeatability and the no-finding control: six proposed process launches total,
not six independent scenarios. Stop on the first missing prerequisite, failed
baseline, drift, wrong hook, timeout, receipt loss, or budget exhaustion. Do not
discard failures and rerun until the expected answer appears.

Require host-enforced limits of five seconds per process, 64 MiB memory, one
process (no descendants), 4096 bytes per output stream and no network. The
mechanics episode, including staging, baselines, replay, cleanup and reporting,
has a ten-minute / twelve-tool-call ceiling; stop sooner if no value remains.
These are proposed ceilings, not permission. A host unable to enforce them is
UNAVAILABLE. A timeout wrapper or Python flags alone do not qualify isolation.

The trusted collector records exact source/contract/driver identities, host and
qualification reference, effect authorization, executable/version/argv/cwd/env,
limit configuration, each exit/stdout/stderr, effect/hook trace, before/after
manifests of originals and tests, reset/replay identity, cleanup observation and
elapsed time/tool costs. Keep each baseline, injection and replay distinct; never
overwrite protected receipts. An untrusted self-reported trace without unchanged
trusted harness and independently collected evidence is insufficient.

| Report status | Meaning |
| --- | --- |
| VIOLATION_OBSERVED | Passing unchanged baseline, valid injection and attributable extra ledger effect, independently reproduced; here only an authored seeded defect, never an observed production problem |
| NO_VIOLATION_OBSERVED | Valid injected condition with no invariant violation in selected scope; no general correctness claim |
| INCONCLUSIVE | Broken baseline/harness, timeout, drift, wrong injection, ambiguous attribution, interrupted cleanup or exhausted budget; never a defect finding |
| UNAVAILABLE | Required host isolation, permission, tool or receipt facility missing; no unsafe fallback |
| NOT_RUN | Proposed condition not executed; retain any known UNAVAILABLE prerequisite separately |

SKIP/DIRECT TEST REVIEW are decisions outside behavior outcome denominators.
KILLED/SURVIVED belong to mutation experiments and cannot label these results.
Do not automatically fix candidates, publish findings, or write outside approved
destinations. PR publication of this authored design is not publication of live
findings or authorization to execute it.

## Comparative gate and decision

Reuse [the existing costed protocol](../IMPLEMENTATION.md#bounded-first-comparison-proposed--not-run)
and [#6](https://github.com/grove/faultline/issues/6); no new evaluator platform.
The public pair above can only check mechanics. The same-pair A/B/C pilot in that
protocol remains NOT RUN and cannot establish independent usefulness. Before a
value comparison, an independent preparer must freeze **fresh** small authored
cases and hidden contract-derived oracles/valid alternatives outside assessor
access. Do not call relabeling these public sources a fresh case. Freeze exact
case count, assignments, hashes, commands, settings, grader and budget allocation
before dispatch; preparation/assessment/grading must be independent. No second
worker or model is launched by this deliverable.

Use A ordinary agent/tests, B explicit negative-case review without injection,
and C the same agent with optional proposed challenge guidance and qualified
execution. Give each arm the same aggregate 15 minutes / 12 tool calls across
its assigned cases, including selection, skips, setup, tests and reporting. Reuse
the two-hour / 60-call total ceiling: 45 minutes / 12 calls shared preparation and
qualification, 45 minutes / 36 calls assessment, 30 minutes / 12 calls independent
validation/report. Mechanics, if included in that episode, consumes these caps;
it is not a free extra budget. A later fresh study needs its own explicit budget.

Grade additional **correctly demonstrated** failures beyond B, useful confirmed
regressions, mistaken accusations (especially on clean controls), and total time
and tool overhead. Retain every assigned assessment including skipped, blocked,
unavailable, NOT_RUN and inconclusive attempts; report denominators, not a success
percentage over completed attempts only. Do not share arm answers or grant C extra
time for setup. Seed knowledge, harness failures and test expectations are not
independent findings.

- **CONTINUE only to a fresh #6 study:** C alone supplies a consequential,
  independently confirmed failure and useful regression, accepts the valid
  control, makes no unsupported accusation and stays within matched caps.
  Even that does not launch an executable product.
- **NARROW:** safety/evidence unavailable or a direct assertion already answers
  the selected question. Retain advice-only guidance and this NOT RUN design.
- **STOP dedicated challenge work:** B supplies the same useful evidence more
  cheaply, costs exceed the cap, or progress requires a general runner. A seeded
  mechanics success alone cannot justify CONTINUE for a product.

**Current recommendation: NARROW.** B's direct assertion is evident by inspection
for this pair; C's incremental practical value is **UNKNOWN**, not measured zero
or proven positive. No comparison or live failure was observed. The sole
[#3 skill](../faultline-audit/SKILL.md) remains advice-only; any future behavioral
expansion must be justified by #9/#10 and fresh #6 evidence, with #2 still a hard
execution gate. No tracker edit or second skill is needed now.

## Current receipt and costs

| Item | Actual state for this design delivery |
| --- | --- |
| Fixture identity | v1 fenced-byte manifest above; enclosing Git commit identifies contract/oracle text |
| Selected baseline/injection/replay processes | 6 proposed / 0 attempted / 0 completed |
| Baseline and injected outcomes | NOT_RUN for both candidates; no effect trace exists |
| Isolation | UNAVAILABLE per retained #2 receipt; no new qualification attempted |
| A/B/C assessments | NOT_RUN; 0 attempted; no findings, regressions validated, false-alarm rate or comparative score |
| Fixture setup/execution/model cost | 0 launches, 0 fixture execution time, 0 additional model dispatches |
| Design/review/packaging overhead | Maintainer suite: 9 checks passed, including static source syntax/hashes; no fixture execution. Total design/review time, tokens and tool cost UNKNOWN; not an experimental arm result |

The #2 receipt is a safety-block receipt only. It must not be cited as a passing
baseline, successful injected condition or observed violation. No claim of
unchanged-source execution is possible when nothing ran. The minimum future
regression remains the two same-key calls and one ledger entry described above.
