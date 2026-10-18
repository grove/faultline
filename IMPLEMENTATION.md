# Faultline — proposed implementation plan

**Status:** Proposed; no installed skill, executable challenge tool, qualified isolation environment, or published effectiveness results exist.

**Product decision pending:** [#9](https://github.com/grove/faultline/issues/9) proposes repositioning Faultline as a **skill-first adversarial correctness challenger**. The initial distinctive hypothesis is **controlled failure-path testing of an unchanged implementation**; targeted mutation testing remains optional for *test strength*. See [README](README.md) and [DESIGN](DESIGN.md).

**Rule:** Build the smallest useful **portable AI skill**, not a new model runner, mutation engine, chaos framework, CLI, or mandatory integration. Extra execution machinery is conditional on observed shortcomings and measured incremental value.

## 0. Decision gate — agree on a small, testable hypothesis

**Issue:** [#9](https://github.com/grove/faultline/issues/9).

First establish the product boundary and the difference between two results:

- **Behavior challenge:** fault-inject a dependency, state or input **without modifying the production implementation** and look for a reproducible violation of a real guarantee.
- **Mutation challenge:** intentionally change production behavior **in a disposable mutant copy** and see whether selected tests detect that particular wrong behavior.

One may demonstrate an implementation defect; the other may demonstrate weak selected tests. Neither certifies correctness. Avoid building a second broad Gapline audit: Gapline already inspects test quality and other risks read-only.

**Required decision record:**
- One-sentence product promise, skill-first interface and two modes: `PLAN` (read-only) and `CHALLENGE` (only if authorized and isolated).
- Named, source-grounded first invariant and the smallest experiment that could refute it.
- Explicit non-goals, exit/stop criteria, limits and relationship to Intentline/Gapline/Proofline.
- Issue-by-issue disposition of #1–#8. Existing work must not silently become an approved roadmap because documentation changed.
- **GO / NARROW / STOP** for the first small prototype. A decision is not a successful audit run.

**Stop if:** the proposed challenge cannot be distinguished from cheaper negative-case review or requires a general-purpose runner to demonstrate even a tiny case.

## 1. Milestone A — one usable, small, optional skill (read-only first)

**Reuse/rescope:** [#3](https://github.com/grove/faultline/issues/3). The working name `faultline-challenge` is **provisional** until a real skill and verified installation exist; do not claim the older `faultline-audit` name is a shipped interface.

**Proposed files after decision:**

```text
faultline/
  README.md
  DESIGN.md
  IMPLEMENTATION.md
  LICENSE
  faultline-challenge/
    SKILL.md
    references/
      challenges.md            # only if a short optional reference helps
  tests/
    test_skill.py              # portable packaging/instruction checks
```

Start with **one canonical root-level skill** and minimal frontmatter so existing agent hosts can discover it. No extra model, runtime Python package, always-on process, downloaded dependencies or cross-project installation. Optional references must be lean, not a catalogue of mandatory checks.

### Skill behavior

1. Determine whether there is a consequential unresolved correctness guarantee; identify the source/caller and exact candidate. For trivial or obvious cases, recommend **SKIP / DIRECT TEST**.
2. Prefer a cheap direct negative/boundary assertion or requirement clarification before proposing an injected failure.
3. For a remaining material uncertainty, name **one** fault condition, how the existing test hook reaches it, a valid alternative outcome, and the observable distinguishing result. Source ground the invariant; mark missing authority **UNKNOWN**.
4. Default to **PLAN / PROPOSED — NOT RUN** when execution is unapproved or the host boundary unqualified.
5. Offer `CHALLENGE` steps **only conditionally**: exact authorized commands, stable snapshot, actually qualified isolation, bound resources, unchanged control, one perturbation and evidence recording. A skill cannot enforce these conditions.
6. Return a short report with identity, what was proposed/observed, raw bounded evidence if present, caveats, actual work/cost and the smallest useful next test. No auto-fix, publication, or unsupported assurance.

### Acceptance checks

- [ ] Real skills-CLI install/discovery or documented direct-file invocation **actually checked** on a named host; installation alone is not proof an agent invoked the skill.
- [ ] Portable instructions and links are valid; no speculative install command in public README.
- [ ] Honest read-only operation is useful even when isolation/commands are unavailable.
- [ ] The skill does not authorize commands, dependency installs, network, file writes, secondary model calls or publishing merely by being loaded.
- [ ] Correct distinction: actual unchanged-code failure versus mutation survivor versus test/harness/setup failure.
- [ ] Low-risk work, unknown contract, unreachable injection, and obviously missing assertion produce a cheap skip or scoped plan, not an experiment ritual.
- [ ] No required new schema, score, multi-agent step, Gapline/Intentline/Proofline adapter or platform.

**Stop if:** the skill cannot describe an actionable, discriminating failure scenario without fabricating authority or claiming it ran tests.

## 2. Milestone B — qualify one real execution boundary

**Required before any live challenge:** [#2](https://github.com/grove/faultline/issues/2). **This issue and this plan do not authorize running tests.**

Running normal tests or injected-failure harnesses can execute arbitrary project code. A copy, worktree, container label or instruction file is **not** sufficient isolation.

On the **specific intended agent host**, independently qualify:

- Protection against modifying the source candidate, retained evidence and unrelated files.
- Denial of access to private files, real credentials and disallowed network/external effects.
- Handling of symlinks, submodules, package scripts, discovery hooks, test fixtures, caches, child processes and path escape attempts.
- Finite wall-clock/process/output budgets, deterministic setup/reset, cleanup restricted to created artifacts, and safe treatment of tool absence.
- Explicit authorizations for candidate selection, exact argv/working directory, fixture reads, writes, output destination, resources, any model/tool expense and network effects.

Run **benign synthetic negative controls** using host-observed receipts, never real secrets or actual external payment/services. Record allowed/denied behavior and telemetry gaps rather than claiming a sandbox because the tests passed.

**Fail-closed invariant:** if isolation or authorized commands cannot be demonstrated, execute **nothing** and return `UNAVAILABLE` with the read-only challenge plan. No unprotected shell fallback.

**Gate:** complete host-specific safety qualification or **NO GO** for executable Milestone C. Packaging tests do not substitute for this gate.

## 3. Milestone C — deterministic Python fault-injection spike

**Issue:** [#10](https://github.com/grove/faultline/issues/10). Start with **one** local Python fixture, not a general injection framework.

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

- [ ] Authored expected controls and source/oracle frozen **before** running any agent evaluation.
- [ ] Real execution permitted only after #2 qualifies that actual host.
- [ ] A completed, qualified run (if authorized) distinguishes a violation from a valid implementation **without changing the production candidate**.
- [ ] An observed result is never inferred from a fixture label or an imagined transcript; every claim links to a genuine receipt.
- [ ] Advice-only `NOT_RUN` and fail-closed `UNAVAILABLE` are meaningful deliverables if execution is not qualified.
- [ ] No hidden build/install, public deployment, auto-remediation, network call, or new fault-injection engine.

**Stop/adjust if:** setup dominates the value, oracle relies on the implementation being tested, the environment cannot be qualified, or normal direct review would already supply the same useful assertion for less cost.

## 4. Milestone D — prove extra value over simpler agent testing

**Reuse the framework in [#6](https://github.com/grove/faultline/issues/6)**, but update the primary hypothesis from mutation scores/test-gap hunting to independently confirmed **behavioral correctness** improvement. A planted failure in Milestone C establishes mechanics, **not** general usefulness.

Run a small **predeclared feasibility** comparison on fresh, independently prepared Python cases (e.g. four to six initial tasks, including low-risk skip and contract-consistent clean controls). Keep independent grader/oracle and valid alternatives hidden from workers.

| Arm | Same total end-to-end budget |
| --- | --- |
| **A — ordinary** | Same coding agent with ordinary development and self-testing. |
| **B — cheap direct review** | Same agent plus explicit negative/failure-path review and applicable direct tests, no injected faults. |
| **C — optional Faultline** | Same agent plus selective `PLAN`/`CHALLENGE`, counting all isolation/setup, baselines, injected tests, corrections, reporting, stops and skips. |

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

**Current repository** contains only `README.md`, `DESIGN.md`, `IMPLEMENTATION.md` and `LICENSE`. Documentation changes **do not complete** any milestone.

| Issue | Current treatment under the proposed pivot |
| --- | --- |
| [#9](https://github.com/grove/faultline/issues/9) | Product direction decision: do first |
| [#10](https://github.com/grove/faultline/issues/10) | One deterministic Python failure-path challenge: first experiment |
| [#2](https://github.com/grove/faultline/issues/2) | Safety gate mandatory for any executable work |
| [#3](https://github.com/grove/faultline/issues/3) | One portable skill: rescope conditionally rather than duplicate |
| [#6](https://github.com/grove/faultline/issues/6) | Reuse value-comparison protocol; extend scope only if justified |
| [#1](https://github.com/grove/faultline/issues/1), [#4](https://github.com/grove/faultline/issues/4) | Mutation tooling and classifications: defer |
| [#5](https://github.com/grove/faultline/issues/5) | Approved real-project dogfood: defer and rescope |
| [#7](https://github.com/grove/faultline/issues/7), [#8](https://github.com/grove/faultline/issues/8) | Other languages: defer |

**Next smallest action:** resolve #9, specify #10's authoritative fixture/oracle, and qualify #2 for the actual host before any proposed challenge is described as executed. If these gates fail, retain the useful read-only plan or stop rather than broadening scope.

[README](README.md) · [Design](DESIGN.md)
