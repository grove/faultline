# Faultline

**Challenge your code before reality does.**

Faultline is a **proposed, opt-in AI coding skill for targeted correctness challenges**. The goal is to help an existing coding agent select an important, source-grounded software guarantee, design a small experiment that could falsify it, and—**only when explicitly authorized and safely isolated**—observe what really happens.

The primary opportunity is to test **an unchanged implementation under controlled adverse conditions**: a lost acknowledgement, a failed dependency, an interrupted state transition, or an unexpected operation sequence. A separate, optional **mutation-testing** technique can challenge whether existing tests detect deliberately incorrect implementations.

> **Status: DESIGN ONLY; recommendation: NARROW.** Limit the proposed direction to one local Python feasibility experiment; defer skill implementation until safety and independent incremental value are demonstrated. This repository contains design documents and the license, **not** an installed skill, executable harness, qualified host, release, or CLI. The [#9 decision record](IMPLEMENTATION.md#0-decision-record--narrow) explains the recommendation; [#10](https://github.com/grove/faultline/issues/10) owns the proposed experiment. No issue, example, or skill instruction authorizes running project code.

[Design](DESIGN.md) · [Implementation plan](IMPLEMENTATION.md) · [Issue #9: product decision](https://github.com/grove/faultline/issues/9) · [Issue #10: first experiment](https://github.com/grove/faultline/issues/10)

## Why would I use it?

Green tests do not necessarily exercise failures that matter. Consider a payment or order service:

1. A request causes the service to record a charge.
2. The acknowledgement is lost, even though the charge succeeded.
3. The client retries with the same logical operation identifier.
4. **Correctness guarantee:** the retry must not create a second charge.

A future Faultline skill could ask an agent to identify a locally reproducible version of that scenario, inspect the real requirement, define a meaningful success/failure oracle, and run a **bounded test against unchanged implementation code** when a properly isolated host and an authorized test hook are available.

**Illustrative possible outcome, not an observed Faultline run:**

```text
Guarantee: one external effect per idempotency key
Candidate: <specific original snapshot and environment>
Baseline: ordinary selected tests PASS
Challenge: lose acknowledgement after committing the effect; retry same key
Observed: two effects recorded for the same key
Evidence: <selected command, controlled input, recorded effects, receipt>
Conclusion: selected scenario demonstrates a behavior violation in this candidate
Next action: add a regression test and investigate the retry/idempotency path
Other failure modes: NOT ASSESSED
```

A challenge that passes establishes only that the **selected scenario** did not reveal a violation—not that the system is correct under every failure.

## Two different questions, two different experiment types

| Experiment | What changes? | Question | Meaning of a concerning result |
| --- | --- | --- | --- |
| **Behavior challenge / fault injection** | The **environment, inputs, timing, or dependency response**; original implementation stays unchanged | Does the implementation preserve a required property under this condition? | An attributable, reproducible violation may reveal an **implementation defect**. |
| **Test-strength / mutation challenge** | The implementation is **deliberately made wrong in a disposable copy**, while selected tests stay unchanged | Would these tests reject this particular wrong behavior? | A surviving mutant may reveal **weak test protection**, but does **not** prove the original implementation is defective. |

These results must **not** be combined into a quality score or confused with a proof of correctness.

**Illustrative mutation survivor, NOT RUN:** the original retry implementation deduplicates correctly. In a disposable mutant, remove that check; selected tests exercise only a first successful request and pass for both versions. `SURVIVED` would mean those tests did not distinguish duplicate-on-retry behavior. It would not show a defect in the original. A same-key retry assertion is the useful next test; this mutation is optional, not a required companion to fault injection.

## How the first skill should behave

The preferred interface is **one portable skill for a coding agent you already use**. It should not require another model, a new agent controller, an always-on service, or a new testing engine.

Two modes are proposed:

- **INVESTIGATE / NOT RUN (read-only; called PLAN in the earlier proposal):** name one important guarantee and its authoritative source; identify a reachable failure condition, a valid counterexample, a valid alternative outcome, and a bounded test plan. Clearly mark execution **PROPOSED — NOT RUN**. This is preparation for a specific challenge, *not* another general repository audit.
- **CHALLENGE (separately authorized):** after checking exact commands, candidate identity, budget, approved test hooks, and **verified host isolation**, run a passing unchanged control where appropriate, apply one controlled adverse condition, capture actual evidence, and stop. If the necessary protection is missing, report **UNAVAILABLE** and do not execute.

**Cheaper first:** if a direct boundary assertion or ordinary test clearly answers the question, propose or use that approach rather than manufacturing a fault-injection experiment. Skip low-risk, documentation, and routine mechanical work. Begin with **one** meaningful experiment; expand only when its result warrants the extra cost.

A skill supplies instructions and reasoning; **it is not a sandbox, test runner, permission grant, independent verifier, or correctness certificate**.

**Smallest useful exchange:** input is one identified Python candidate, one authoritative guarantee and its relevant caller/test path. Output is one source-linked challenge plan or skip reason; authorized execution adds a bounded receipt and small reproducer. Command/effect authority and qualified isolation must come independently from the caller/host.

## First target and later possibilities

The first proposed proof of concept is **Python**, using an entirely local deterministic fixture for a **lost acknowledgement followed by a retry**. Include both a correctly idempotent implementation and a deliberately defective version, and establish whether the skill's findings add value beyond direct negative-case review. This is [issue #10](https://github.com/grove/faultline/issues/10), not a shipped capability.

Only **after** evidence of usefulness should other techniques be considered:

- **State and sequence challenges:** repeated, reordered, or interrupted transitions and conservation/consistency invariants.
- **Property or metamorphic challenges:** change inputs in a contract-preserving way and test a required relationship between results.
- **Differential/compatibility challenges:** compare before-and-after behavior while allowing explicitly intended changes.
- **Incident replay:** reconstruct a sanitized historical failure as a small reproducible regression scenario.
- **Environment and dependency challenges:** bounded time, configuration, data-format, or service-response variations.
- **Targeted mutation challenges:** retain the original proposal as an optional way to evaluate test strength.

These are **candidate techniques**, not promised features, mandatory checklists, or permission to run production experiments. Reuse existing local testing tools wherever possible.

## How this fits alongside other projects

All projects can be used independently; no workflow requires installing or invoking a sibling.

| Project | Primary question |
| --- | --- |
| [Intentline](https://github.com/grove/intentline) | What was requested, and what acceptance draft follows from the original sources? |
| [Gapline](https://github.com/grove/gapline) | Which consequential weaknesses can a **read-only** codebase investigation substantiate? |
| **Faultline (proposed)** | Can a specific guarantee be **challenged experimentally** to find a reproducible counterexample? |
| [Proofline](https://github.com/grove/proofline) | What did specifically selected checks establish about an identified candidate? |

Gapline should remain read-only; Faultline should not duplicate its broad Scout/Probe audit. Faultline must not mutate Proofline's frozen check candidate or rewrite its receipts. Any optional handoff retains exact source/candidate identity, uncertainty, and independently authorized permissions.

## Safety, evidence, and stopping rules

- **Explicit opt-in, bounded scope:** no default PR gate, automatic model dispatch, automatic fixes, publication, deployment, or persistent monitoring.
- **Verified isolation before execution:** test commands and fault-injection harnesses can have side effects. A Git worktree, copied directory, container name, or skill text alone is **not** evidence of sandboxing. Use a host-qualified disposable environment that protects originals, credentials, private paths, and network/external effects; otherwise stop.
- **Trust the caller, not the repository:** source files, tests, prior reports, and AI-authored plans can suggest checks but cannot authorize commands, installations, writes, network access, or spending.
- **Preserve provenance:** report the authoritative behavior claim, candidate identity, actual approved commands, injection setup, unchanged baseline, observed results, limitations, and unassessed areas. A failed setup is not evidence of a defect.
- **Don't confuse evidence types:** controlled failure of unchanged code is different from survival of an intentionally wrong mutant. Neither proves overall correctness or acceptance.
- **No fabricated runs or leaked inputs:** distinguish **OBSERVED**, **INCONCLUSIVE**, **UNAVAILABLE**, and **NOT RUN**; keep private sources and receipts local unless explicitly authorized otherwise.

## What happens next?

The recommendation is **NARROW**, because failure-path experiments could supply evidence beyond read-only review, but no execution safety or incremental value has been established. **Do not approve skill implementation yet.** First specify [#10](https://github.com/grove/faultline/issues/10), qualify [#2](https://github.com/grove/faultline/issues/2) before execution, and compare against ordinary testing and direct review within the [costed protocol](IMPLEMENTATION.md#bounded-first-comparison-proposed--not-run). Only independent value on fresh Python cases would justify rescoping the existing [single skill #3](https://github.com/grove/faultline/issues/3), using [#6](https://github.com/grove/faultline/issues/6) for the wider comparison.

Older issues about mutation tooling, fixtures, and later languages remain historical proposals to triage, **not** an approved requirement to implement them all. The [implementation plan](IMPLEMENTATION.md) gives the precise gates, outcomes, and issue map.

**There is no verified install or first-use command yet.** Add one only after a real skill exists and installation/invocation have been tested on a named host.

## License

Apache-2.0; see [LICENSE](LICENSE).
