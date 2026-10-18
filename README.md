# Faultline

**Challenge your code before reality does.**

Faultline provides one **opt-in, advice-only test-strength skill** for an existing coding agent: [faultline-audit/SKILL.md](faultline-audit/SKILL.md). It first recommends a useful negative/boundary assertion or a justified skip. Only a material unresolved question warrants a non-executing mutation plan.

The broader proposed direction is to test **an unchanged implementation under controlled adverse conditions**: a lost acknowledgement, a failed dependency, an interrupted state transition, or an unexpected operation sequence. This remains deferred. Mutation testing asks a separate question: whether existing tests detect deliberately incorrect implementations.

> **Status: advice-only skill; execution NO_GO.** [#3](https://github.com/grove/faultline/issues/3) permits this read-only release before safety qualification. No qualified host, mutation backend, executable harness, CLI, or demonstrated incremental effectiveness is supplied. The earlier [#9 NARROW recommendation](IMPLEMENTATION.md#0-decision-record--narrow) remains the historical basis for deferring experiments and the broader product. No issue, example, installation, or skill instruction authorizes running project code.

[Design](DESIGN.md) · [Implementation plan](IMPLEMENTATION.md) · [Issue #9: product decision](https://github.com/grove/faultline/issues/9) · [#10 frozen spike design — NOT RUN](experiments/lost-acknowledgement.md)

[#2's host qualification](ISOLATION.md) supplies the bounded threat model,
permissions and synthetic negative controls. On the actual macOS agent host,
all twelve native sandbox launches failed before a child started. The retained
[receipt](qualification/2026-10-18-macos.json) establishes **UNAVAILABLE**, not
protected-file or network denials. No execution is enabled; closing an issue or
copying the skill cannot qualify a host.

The subsequent [Apple Container preflight](ISOLATION.md#next-candidate-apple-container--unavailable-before-setup)
selects one next candidate but finds no installed CLI; setup and synthetic launches
remain unapproved. Its [inspection receipt](qualification/2026-10-18-apple-container-preflight.json)
records **UNAVAILABLE**, zero boundary launches and all controls **NOT RUN**.
Docker client/app presence is not qualification. #2 remains open.

## Use the skill

No runtime dependency or installation is required. Ask your existing agent:

```text
Read /absolute/path/to/faultline/faultline-audit/SKILL.md and apply it advice-only
to <exact candidate and relevant caller/test paths> for <behavior and source>.
Prefer SKIP or a direct assertion. Do not execute project code or edit files.
```

For example, a documentation-only change should get **SKIP** with its low-risk
reason. An obvious missing retry assertion should get **DIRECT TEST REVIEW**,
with a concrete same-key input and expected effect count. Neither decision is a
mutation outcome. If a mutant would answer a material unresolved question, expect
one **PROPOSED — NOT_RUN** plan. An execution request gets **NO_GO / UNAVAILABLE**
with the missing qualification and a useful non-executing alternative.

For repository-scoped Codex discovery, run this from your Faultline checkout;
replace the target with an existing project you choose. It refuses an existing
destination rather than replacing your installed skill:

```sh
target=/absolute/path/to/your/project
mkdir -p "$target/.agents/skills" &&
  test ! -e "$target/.agents/skills/faultline-audit" &&
  test ! -L "$target/.agents/skills/faultline-audit" &&
  cp -R faultline-audit "$target/.agents/skills/faultline-audit"
```

Open Codex in that project and select/invoke `$faultline-audit` with the same
candidate, question, and advice-only constraint. If discovery does not refresh,
restart Codex or use the direct-file prompt. Other hosts can read the standalone
file; their native discovery/install mechanisms have not been verified here.
The checkout keeps **one canonical skill**; an installation is a user-owned copy
that must be recopied deliberately for updates. No sibling project is required.

**Verified on 2026-10-18:** macOS 27.0.1 arm64, Codex CLI 0.163.0. A disposable
project received a byte-identical copy using `cp -R`; the local app-server's
`skills/list` discovered `faultline-audit`, enabled in repository scope, at the
copied path. Direct-file reading and the documentation-only SKIP path were checked
by the existing agent. No extra model turn or target test/mutant was launched.
Discovery is not proof of agent invocation or experiment safety. See the official
[Codex skill locations](https://developers.openai.com/codex/skills/) and
[discovery API](https://developers.openai.com/codex/app-server/).

Maintainer packaging regression checks (Python standard library only):

```sh
python3 -B -m unittest discover -s tests -v
```

These inspect metadata, links, copying, critical instruction boundaries, frozen
spike source hashes/syntax and the synthetic probe's failure classification/finite
leader timeout. They do not execute the spike's fenced source blocks or run
target-project code or qualify [#2](https://github.com/grove/faultline/issues/2).

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

The interface is **one portable skill for a coding agent you already use**. The current `faultline-audit` release supplies focused read-only test review and mutation plans. It requires no other model, agent controller, service, or testing engine. The broader correctness-challenge design below remains proposed.

Two modes are proposed:

- **INVESTIGATE / NOT RUN (read-only; called PLAN in the earlier proposal):** name one important guarantee and its authoritative source; identify a reachable failure condition, a valid counterexample, a valid alternative outcome, and a bounded test plan. Clearly mark execution **PROPOSED — NOT RUN**. This is preparation for a specific challenge, *not* another general repository audit.
- **CHALLENGE (separately authorized):** after checking exact commands, candidate identity, budget, approved test hooks, and **verified host isolation**, run a passing unchanged control where appropriate, apply one controlled adverse condition, capture actual evidence, and stop. If the necessary protection is missing, report **UNAVAILABLE** and do not execute.

**Cheaper first:** if a direct boundary assertion or ordinary test clearly answers the question, propose or use that approach rather than manufacturing a fault-injection experiment. Skip low-risk, documentation, and routine mechanical work. Begin with **one** meaningful experiment; expand only when its result warrants the extra cost.

A skill supplies instructions and reasoning; **it is not a sandbox, test runner, permission grant, independent verifier, or correctness certificate**.

**Smallest useful exchange:** input is one identified candidate, one authoritative guarantee and its relevant caller/test path. Current output is a source-linked direct assertion, mutation plan, or skip reason. A future qualified, separately authorized executable version could add receipts; the current skill does not execute.

## First target and later possibilities

The first proposed proof of concept is **Python**, using an entirely local deterministic fixture for a **lost acknowledgement followed by a retry**. [Issue #10's frozen design](experiments/lost-acknowledgement.md) supplies exact correct/defective source blocks, a transport hook, independent expected outcomes and a bounded execution/comparison plan. Execution is **UNAVAILABLE / NOT RUN**; the known seeded pair already has an obvious direct regression assertion. Incremental value beyond negative-case review remains unmeasured. This is a design deliverable, not a shipped challenge capability.

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
| **Faultline** | Would selected tests detect a specific wrong behavior? Advice-only now; broader correctness experiments remain proposed. |
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

The earlier **NARROW** recommendation remains relevant to executable correctness challenges: no execution safety or incremental value has been established. This release implements #3's explicitly permitted advice-only scope and [#10's NOT RUN design](experiments/lost-acknowledgement.md). Qualify [#2](https://github.com/grove/faultline/issues/2) before execution, and compare against ordinary testing and direct review within the [costed protocol](IMPLEMENTATION.md#bounded-first-comparison-proposed--not-run). Independent value on fresh Python cases under [#6](https://github.com/grove/faultline/issues/6) would be needed to justify the broader executable skill.

Older issues about mutation tooling, fixtures, and later languages remain historical proposals to triage, **not** an approved requirement to implement them all. The [implementation plan](IMPLEMENTATION.md) gives the precise gates, outcomes, and issue map.

Use the [verified copy/discovery and direct-file instructions](#use-the-skill) above for this advice-only skill. Installation never unlocks execution.

## License

Apache-2.0; see [LICENSE](LICENSE).
