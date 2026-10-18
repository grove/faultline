# Faultline — proposed implementation plan

**Status:** #3's advice-only [faultline-audit](faultline-audit/SKILL.md) is implemented, with verified copying/discovery and packaging checks. [#10's frozen fixture/protocol design](experiments/lost-acknowledgement.md) is delivered **UNAVAILABLE / NOT RUN**. No executable challenge tool, qualified isolation environment/backend, or published effectiveness results exist.

**Product recommendation for [#9](https://github.com/grove/faultline/issues/9): NARROW.** Retain the skill-first correctness-challenge hypothesis, limited to one Python feasibility experiment. The subsequent #3 implementation request selects its explicitly permitted advice-only scope; executable skill work remains deferred until safety and independent value are demonstrated. Targeted mutation testing remains optional for *test strength*. See [README](README.md) and [DESIGN](DESIGN.md).

**Rule:** Build the smallest useful **portable AI skill**, not a new model runner, mutation engine, chaos framework, CLI, or mandatory integration. Extra execution machinery is conditional on observed shortcomings and measured incremental value.

## 0. Decision record — NARROW

**Historical record:** this section preserves #9's recommendation and evidence at
that decision. The later #3 advice-only implementation does not complete any
safety, mechanics, or independent-value milestone or authorize experiments.

**Issue:** [#9](https://github.com/grove/faultline/issues/9). **Recommendation date:** 2026-10-18. **Evidence state:** design inspection only; experiments **NOT RUN**, execution qualification **UNAVAILABLE** in this repository. This recommendation does not approve a product pivot, skill build or experiment execution.

**Purpose:** Faultline helps an existing coding agent seek a reproducible counterexample to one source-grounded correctness guarantee through a bounded, separately authorized experiment against unchanged implementation code.

**Why NARROW:** an observed failure under a controlled adverse condition could add evidence beyond Gapline's read-only investigation. No observed host qualification or independent comparison currently demonstrates that advantage. GO for a skill is premature; STOP is warranted if ordinary testing/direct review supplies the same actionable regression more cheaply. The existing [#10](https://github.com/grove/faultline/issues/10) is sufficient to investigate; no new build issue or runtime is needed.

**Smallest exchange:** one candidate identity, authoritative guarantee and reachable caller/test path in; one source-linked plan or skip reason out. `INVESTIGATE / NOT RUN` (formerly `PLAN`) is non-executing. `CHALLENGE` additionally requires independent caller/host effect authorization, exact commands, passing unchanged controls and observed #2 isolation qualification; output adds a bounded receipt and small reproducer. Missing protection means **UNAVAILABLE**, never shell fallback. Skip low-risk work, obvious direct assertions, unknown contracts and unreachable or disproportionately costly setups.

**Evidence distinction:** an attributable invariant violation in unchanged code can demonstrate a selected behavior failure. A deliberately wrong mutant surviving selected unchanged tests shows only weak detection of that difference, after considering equivalence and reachability. Neither certifies correctness. The [README examples](README.md#two-different-questions-two-different-experiment-types) are illustrative, **NOT RUN**; mutation is not a mandatory second step.

**Source basis:** the [#9 request](https://github.com/grove/faultline/issues/9), [repository proposal at `00c9834`](https://github.com/grove/faultline/tree/00c9834e45962d44ee85855935040bac973c0dc2), and the current #1–#8/#10 issue bodies inform this recommendation. They supply design requirements, not observed effectiveness or execution authority. Preserve Gapline's read-only scope and Proofline's frozen candidates/receipts; no sibling integration or changes.

**Proposed order:** specify #10 → qualify #2 → one bounded comparison → fresh independent value check using #6 → reconsider #3. The numbered milestones below describe conditional work, not permission or build order. No skill, harness, dependencies, extra model dispatch, project-code execution or tracker edits are part of #9.

## 1. Milestone A — one usable, small, optional skill (read-only first)

**Implemented narrowly under #3:** a read-only test-strength skill can ship before safety qualification. This does not implement the broader INVESTIGATE/CHALLENGE product proposed below. Executable expansion still requires #10's mechanics and a fresh independent comparison using #6, plus #2 host qualification and explicit effect authorization.

**Canonical interface:** [#3](https://github.com/grove/faultline/issues/3), `faultline-audit/SKILL.md`. The earlier `faultline-challenge` working name is not an additional skill.

**Current files:**

```text
faultline/
  README.md
  DESIGN.md
  IMPLEMENTATION.md
  LICENSE
  faultline-audit/
    SKILL.md
  tests/
    test_skill.py              # portable packaging/instruction checks
```

Start with **one canonical root-level skill** and minimal frontmatter so existing agent hosts can discover it. No extra model, runtime Python package, always-on process, downloaded dependencies or cross-project installation. Optional references must be lean, not a catalogue of mandatory checks.

### Broader future skill behavior (conditional)

The current skill stops at advice: up to three concrete direct assertions or a
useful SKIP; one targeted mutation plan only for material remaining uncertainty;
NO_GO / UNAVAILABLE for execution. It preserves the production-only mutation,
unchanged baseline/test identities, independent reset, six outcome categories,
denominators and actual overhead requirements in a **non-executing** protocol.

1. Determine whether there is a consequential unresolved correctness guarantee; identify the source/caller and exact candidate. For trivial or obvious cases, recommend **SKIP / DIRECT TEST**.
2. Prefer a cheap direct negative/boundary assertion or requirement clarification before proposing an injected failure.
3. For a remaining material uncertainty, name **one** fault condition, how the existing test hook reaches it, a valid alternative outcome, and the observable distinguishing result. Source ground the invariant; mark missing authority **UNKNOWN**.
4. Default to **INVESTIGATE / PROPOSED — NOT RUN** when execution is unapproved or the host boundary unqualified.
5. Offer `CHALLENGE` steps **only conditionally**: exact authorized commands, stable snapshot, actually qualified isolation, bound resources, unchanged control, one perturbation and evidence recording. A skill cannot enforce these conditions.
6. Return a short report with identity, what was proposed/observed, raw bounded evidence if present, caveats, actual work/cost and the smallest useful next test. No auto-fix, publication, or unsupported assurance.

### Acceptance checks

- [x] Byte-identical copy and Codex CLI 0.163.0 app-server discovery checked on macOS 27.0.1 arm64; direct-file reading and documentation-only SKIP checked by the existing agent. No new model turn. Discovery alone is not proof an agent invoked the skill.
- [x] Standalone links, metadata, copying and critical instruction boundaries have standard-library regression checks; verified copy and first-use guidance is in README.
- [ ] Honest read-only operation is useful even when isolation/commands are unavailable.
- [ ] The skill does not authorize commands, dependency installs, network, file writes, secondary model calls or publishing merely by being loaded.
- [ ] Correct distinction: actual unchanged-code failure versus mutation survivor versus test/harness/setup failure.
- [ ] Low-risk work, unknown contract, unreachable injection, and obviously missing assertion produce a cheap skip or scoped plan, not an experiment ritual.
- [ ] No required new schema, score, multi-agent step, Gapline/Intentline/Proofline adapter or platform.

**Stop if:** the skill cannot describe an actionable, discriminating failure scenario without fabricating authority or claiming it ran tests.

## 2. Milestone B — qualify one real execution boundary

**Observed #2 result:** [host qualification and threat model](ISOLATION.md), with
[native receipts](qualification/2026-10-18-macos.json). This macOS agent host
refused every native sandbox launch before child startup: **UNAVAILABLE**.
Original synthetic source/tests/receipt hashes remained unchanged after every
attempt. Actual effect denial, descendant containment and resource limits remain
unestablished; no project execution or Milestone C authorization follows.

**Next #2 iteration:** [Apple Container preflight](ISOLATION.md#next-candidate-apple-container--unavailable-before-setup)
selects one next candidate, with [read-only inspection evidence](qualification/2026-10-18-apple-container-preflight.json).
The CLI is not found; setup and synthetic launches are unapproved. Zero new
boundary launches; all controls NOT RUN / UNQUALIFIED. Keep #2 open and obtain
exact host/setup approval before a separately authorized synthetic protocol.

**Required before any live challenge:** [#2](https://github.com/grove/faultline/issues/2). **This issue and this plan do not authorize running tests.**

Running normal tests or injected-failure harnesses can execute arbitrary project code. A copy, worktree, container label or instruction file is **not** sufficient isolation.

On the **specific intended agent host**, independently qualify:

- Protection against modifying the source candidate, retained evidence and unrelated files.
- Denial of access to private files, real credentials and disallowed network/external effects.
- Handling of symlinks, submodules, package scripts, discovery hooks, test fixtures, caches, child processes and path escape attempts.
- Injected-failure hooks and fakes themselves: post-commit acknowledgement suppression, exceptions, retry/reset paths and cleanup must not escape the boundary, alter protected source/receipts or contact real services.
- Finite wall-clock/process/output budgets, deterministic setup/reset, cleanup restricted to created artifacts, and safe treatment of tool absence.
- Explicit authorizations for candidate selection, exact argv/working directory, fixture reads, writes, output destination, resources, any model/tool expense and network effects.

Run **benign synthetic negative controls** using host-observed receipts, never real secrets or actual external payment/services. Record allowed/denied behavior and telemetry gaps rather than claiming a sandbox because the tests passed.

**Fail-closed invariant:** if isolation or authorized commands cannot be demonstrated, execute **nothing** and return `UNAVAILABLE` with the read-only challenge plan. No unprotected shell fallback.

**Gate:** complete host-specific safety qualification or **NO GO** for executable Milestone C. Packaging tests do not substitute for this gate.

## 3. Milestone C — deterministic Python fault-injection spike

**Issue:** [#10](https://github.com/grove/faultline/issues/10). Start with **one** local Python fixture, not a general injection framework.

**Design delivered:** [lost-acknowledgement v1](experiments/lost-acknowledgement.md)
freezes exact source blocks and hashes, the authored contract, transport hook,
oracle/contrary outcomes, proposed argv, receipts, budgets and decision gate.
These blocks are data, not executed fixtures. The #2 host remains UNAVAILABLE;
all baselines, injections and assessments are NOT RUN. Current recommendation is
NARROW: direct same-key review already identifies the seeded regression, and no
independent practical advantage over B has been measured. The historical proposed
comparison below is retained; its public seeded pair can establish mechanics
only. Fresh withheld cases and independent judgments are required for value.

### Contract and controls

- Source-grounded invariant for the authored fixture: **the same logical payment/order operation identifier causes at most one external effect**, even if a post-commit acknowledgement is lost and the caller retries.
- Use an in-memory fake ledger/service; no real money, private data, payment API, network fault injection or production system.
- Freeze **two intentionally different implementations** before the experiment: one valid idempotent path and one deliberately defective double-application path. Keep an independently authored oracle withheld from worker contexts during comparative evaluation.
- A deterministic test hook loses the acknowledgement **after** the first effect is committed. Retry with the same key; inspect the actual recorded effects, not merely the returned status.
- Verify unchanged normal/control behavior; run the failure scenario against the **unchanged source for each fixture**. Fault injection may modify the test harness/environment, **not** the implementation being judged.
- Prefer one bounded challenge, expanding only when a second independent hypothesis is justified. No sleeps/races as a substitute for a controlled synchronization mechanism.

### Required honest controls

| Control | Correct reporting |
| --- | --- |
| Defective fixture yields two effects under the injected failure | `VIOLATION_OBSERVED`, attributable to this qualified scenario only |
| Valid fixture yields one effect under identical failure | `NO_VIOLATION_OBSERVED`, not universal correctness |
| Caller contract unclear or fixture cannot reach commit/ack boundary | `INCONCLUSIVE` or `NOT_RUN` with the missing assumption |
| Baseline already broken/flaky, hook fails, receipt incomplete | `INCONCLUSIVE` / `UNAVAILABLE`; no verdict based on noise |
| Isolation missing or permission not provided | `UNAVAILABLE`; **no execution** |
| Obvious direct assertion or low-risk scenario needs no injection | `SKIPPED` decision, not a mutation/test outcome |

For any executed case retain exact original bytes/identity, authorization, commands, verified safety boundary, injection configuration, baseline, observed side-effect sequence, meaningful opposite result, elapsed/tool cost and original-source post-check. Count not-run attempts and failures; do not silently discard inconvenient episodes.

### Acceptance

- [x] Authored expected controls and source/oracle frozen in the [v1 design](experiments/lost-acknowledgement.md) **before** any agent evaluation; no evaluation attempted.
- [ ] Real execution permitted only after #2 qualifies that actual host.
- [ ] A completed, qualified run (if authorized) distinguishes a violation from a valid implementation **without changing the production candidate**.
- [ ] An observed result is never inferred from a fixture label or an imagined transcript; every claim links to a genuine receipt.
- [ ] Advice-only `NOT_RUN` and fail-closed `UNAVAILABLE` are meaningful deliverables if execution is not qualified.
- [ ] No hidden build/install, public deployment, auto-remediation, network call, or new fault-injection engine.

**Stop/adjust if:** setup dominates the value, oracle relies on the implementation being tested, the environment cannot be qualified, or normal direct review would already supply the same useful assertion for less cost.

### Bounded first comparison (PROPOSED — NOT RUN)

Use **only the lost-acknowledgement/retry scenario**, with the two frozen authored implementations above. #10 supplies the fixture's intended guarantee; an independent preparer must fix the actual fixture contract before any run. Observe ledger entries for one key: normal first request yields one effect for both candidates; commit then lose acknowledgement and retry yields one effect for the valid candidate, two for the defective candidate. A rejected retry that preserves one effect is also valid; a harness error is not a violation. No mutation, second state-transition case or production target is needed.

Compare three isolated assessments of the **same pair**, using the same existing agent/host/model settings and source access, without sharing answers between arms. This specifies future assessments, not additional worker/model dispatch now:

| Arm | Selected work; 15 minutes and 12 tool calls total per arm, including both candidates |
| --- | --- |
| A | Ordinary testing and normal agent review. |
| B | Explicit focused negative/retry-case review and ordinary direct assertions; no injected fault. This is the cheaper comparator. |
| C | A short proposed INVESTIGATE/CHALLENGE protocol, not an installed skill; at most one deterministic injected condition per candidate, only if cheaper review leaves uncertainty. |

Predeclare a **two-hour / 60-tool-call ceiling** for the whole pilot: at most 45 minutes/12 calls for independent fixture/oracle preparation and #2 qualification, 45 minutes/36 calls for A/B/C together, and 30 minutes/12 calls for independent validation/reporting. Report shared preparation separately; charge all arm-specific setup (including C's hook work), baselines, selection/skips, executions, corrections and reporting to that arm's equal cap. Within each arm, cap challenge execution at ten minutes and each test process at five seconds, with host-enforced cleanup. Use installed stdlib Python tools; no installs, extra models or paid services. Exact commands/host still need separate authorization. If qualification or preparation cannot fit, stop **UNAVAILABLE**; do not silently move cost outside the budget. Any later study needs a new explicit budget.

Before assessment, freeze candidate bytes, fixture contract, expected normal/fault outcomes, valid alternatives, host/tool settings, command permissions, hidden evaluator oracle and grader. Hide variant labels/expected answers from assessment contexts; keep preparation and independent grading separate from the assessed work. Six candidate assessments are assigned (two per arm), **not six independent scenarios**. Retain all six denominators, including skips, blocked, timed-out, NOT_RUN and inconclusive results; no favorable reruns or extra time for C.

Each executed receipt must retain source/requirement identity, exact injected post-commit condition, command/argv/tool/version/host, passing unchanged baseline, actual effect sequence, reset/repeat details, original-source post-check, elapsed time/tool calls and limitations. Validate any claimed violation with a small replay against the same unchanged candidate; a useful regression must distinguish the defective path and accept the valid path. Preauthored expectations remain **NOT RUN** until evidenced.

**Falsifier / decision threshold:** if B already identifies the same consequential failure and sufficient regression assertion, C supplies no demonstrated incremental value: **STOP the dedicated skill path or NARROW to direct-test guidance**. If C alone provides an independently validated failure/reproducer and useful regression, accepts the valid control, produces no unsupported defect claim, and stays within the same cap, proceed only to fresh withheld Python cases under #6. A planted success establishes mechanics, not product effectiveness and not approval for #3. Safety/setup failure or ambiguous attribution is **INCONCLUSIVE / UNAVAILABLE**, not evidence for GO. A general runner requirement or cost beyond the cap is a reason to stop this spike.

## 4. Milestone D — prove extra value over simpler agent testing

**Proposed extension to [#6](https://github.com/grove/faultline/issues/6):** retain its mutation comparison and evidence; separately evaluate independently confirmed **behavioral correctness** improvement before approving #3. Its current mutation-specific dependencies (#4/#5) remain attached to that track; a behavioral comparison would instead require #2/#10 mechanics, independent fixture/oracle preparation and separate authorization. This is a proposed scope/dependency revision, not a tracker change or permission to run a study. A planted failure in Milestone C establishes mechanics, **not** general usefulness.

Run a small **predeclared feasibility** comparison on fresh, independently prepared Python cases (e.g. four to six initial tasks, including low-risk skip and contract-consistent clean controls). Keep independent grader/oracle and valid alternatives hidden from workers.

| Arm | Same total end-to-end budget |
| --- | --- |
| **A — ordinary** | Same coding agent with ordinary development and self-testing. |
| **B — cheap direct review** | Same agent plus explicit negative/failure-path review and applicable direct tests, no injected faults. |
| **C — optional Faultline** | Same agent plus selective `INVESTIGATE`/`CHALLENGE` guidance, counting all isolation/setup, baselines, injected tests, corrections, reporting, stops and skips. |

Freeze original request, source bytes, host/model/settings, command permissions, environment, allowed time/tool cost, grading protocol, **acceptable extra overhead** and stop criteria before launches. Randomize order where feasible, do not allow oracle leakage or silent reruns, and include all assigned cases and incomplete attempts.

**Primary:** independent judgment of satisfactory final outcome for the **whole original task**, including valid alternative solutions.

**Secondary:** material implementation defects or durable regression checks C adds *beyond B*, false alarms or valid-design accusations, inconclusive setup, isolation failures, time, tool/model cost, and human verification effort where measured. Keep useful refutations/no findings. Do not use number of scenarios, mutation counts, or report length as substitutes for value.

**Decision:**
- **KEEP OPTIONAL / CONTINUE** only if experiments repeatedly reveal consequential otherwise-missed problems at reasonable total cost with no unsafe effects; expand carefully on fresh holdout tasks.
- **NARROW / SIMPLIFY / STOP** if direct review gives equivalent useful evidence more cheaply or equivalent outcomes create excessive noise.
- **INCONCLUSIVE** if blocked, underpowered, ceiling-limited, or unsafe; do not claim superiority.
- Explicitly label simulated/seeded defects as controls, not production discoveries.

No benchmark result automatically authorizes a custom CLI or runtime.

## 5. Milestone E — dogfood and conditional additional techniques

After qualification and positive evidence, consider **one** approved small real-project snapshot with a maintainer-specified guarantee. See [#5](https://github.com/grove/faultline/issues/5) for older mutation-oriented candidate targets; **re-scope before use**. Get separate source, commands, isolation and budget authorization. Never treat these candidate areas as known defects.

Only then assess techniques **one at a time**:

1. **Property/metamorphic challenges:** input transformation with a source-grounded relation and valid-alternative controls.
2. **Differential/compatibility challenges:** before/after comparison with explicit allowance for intentional differences and legacy data.
3. **Stateful transition sequences or incident replay:** deterministic reproduction, genuine invariant and resettable test setup.
4. **Focused mutation testing:** reuse existing backends only if a concrete test-strength question remains after cheap review; see [#1](https://github.com/grove/faultline/issues/1) and [#4](https://github.com/grove/faultline/issues/4).

Environment/configuration tests, service-contract challenges, language expansion, integrations, and broader chaos-style testing are **ideas, not committed backlog or supported modes**. [Rust #7](https://github.com/grove/faultline/issues/7) and [Java #8](https://github.com/grove/faultline/issues/8) remain deferred until an actual Python benefit and host fit exist.

Each proposed addition needs independent tests of correctness, valid alternatives, false alarms, safety, and **additional value over the existing skill and cheaper workflow**. One negative study is a legitimate reason not to add features.

## 6. Only-if-needed implementation helpers

**Default:** no new runtime, shell utility, orchestration server, persistent schema, CLI, CI gate or automatic PR workflow. Use existing host tools and independently selected test hooks.

Consider a tiny helper **only** if measured skill-only trials reveal a *specific* repeated failure—e.g. nondeterministic replay, unsafe state reset, missing provenance or incorrect attribution—that a small deterministic component would solve. Before building it require a separate threat model, isolated negative controls, measured cost/benefit, and an explicit go decision. More features or cleaner architecture alone are not sufficient.

## 7. Current state and issue map

**Current repository** contains the design documents/license, one canonical `faultline-audit/SKILL.md`, packaging checks, #10's frozen NOT RUN fixture/protocol design, and #2's host-specific threat model, synthetic maintainer probes and failed-launch receipt. #3 implements advice-only test-strength review; no host has qualified for execution. #9's **NARROW recommendation** remains the historical experimental direction. The following future dispositions are proposals; existing issue bodies and states are unchanged.

| Issue | Disposition and retained scope |
| --- | --- |
| [#1](https://github.com/grove/faultline/issues/1) | **DEFER** mutation-backend/metrics selection; unnecessary for the first behavior experiment. Keep read-only research and later optional test-strength tooling scope. |
| [#2](https://github.com/grove/faultline/issues/2) | **RETAIN / EXTEND** the hard actual-host gate to injected-failure hooks, fakes, retries and cleanup as well as mutation tools. No execution until observed qualification and caller authorization. |
| [#3](https://github.com/grove/faultline/issues/3) | **ADVICE-ONLY IMPLEMENTED** at `faultline-audit/SKILL.md`; no execution. A broader executable rescope still requires qualified safety, #10 mechanics and fresh #6 value evidence. |
| [#4](https://github.com/grove/faultline/issues/4) | **RETAIN / DEFER** mutation qualification and native outcome evidence; it is not replaced by #10 and is not required for unchanged-code experiments. |
| [#5](https://github.com/grove/faultline/issues/5) | **DEFER** real-project dogfood until safety/mechanics/value are established; rescope one guarantee later. Listed Proofline/Intentline areas are proposed targets, not known defects or access permission. |
| [#6](https://github.com/grove/faultline/issues/6) | **RETAIN / PROPOSE EXTENSION** of the same-budget independent comparison to behavior challenges. Preserve mutation results; revise dependencies explicitly for that track rather than require deferred #4/#5 before a synthetic value check. |
| [#7](https://github.com/grove/faultline/issues/7) | **DEFER** Rust tooling discovery/execution until useful Python evidence and separately approved host/scope/budget. No automatic language expansion. |
| [#8](https://github.com/grove/faultline/issues/8) | **DEFER** Java discovery/execution; retain Python-value and Rust-feasibility prerequisites. No current Java work. |
| [#9](https://github.com/grove/faultline/issues/9) | **NARROW recommendation delivered** by this historical design record; no experimental effectiveness or execution approval follows from the later advice-only #3 implementation. |
| [#10](https://github.com/grove/faultline/issues/10) | **DESIGN DELIVERED / NARROW** in the [frozen spike](experiments/lost-acknowledgement.md); execution UNAVAILABLE / NOT RUN. No independent value demonstrated or execution enabled. |

None of #1–#8 needs a duplicate or automatic closure. The standalone mutation-first roadmap becomes redundant as the default path; its optional test-strength work and evidence remain useful. [Gapline #17](https://github.com/grove/gapline/issues/17) and [#18](https://github.com/grove/gapline/issues/18) remain independent read-only ideas, with no dependency or automatic integration.

**Next smallest action:** review the frozen #10 design; qualify #2 on an independently authorized host before any experiment. If the costed comparison finds no advantage over direct review, stop the skill path. No new runtime or language work follows automatically.

[README](README.md) · [Design](DESIGN.md)
