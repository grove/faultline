# Faultline — proposed skill-first design

**Status:** Design only; [#9 recommendation: NARROW](IMPLEMENTATION.md#0-decision-record--narrow) to one Python feasibility experiment. No implemented skill, fault-injection runner, qualified execution host, or demonstrated effectiveness; skill implementation remains deferred.

**Thesis:** **Challenge your code before reality does.** Help an existing AI coding agent identify one important, source-grounded guarantee and select the **smallest controlled experiment** that could falsify it. Run the experiment only with explicit authorization and a verified isolated host; otherwise provide an honest, read-only plan.

This reframes the earlier mutation-only proposal. **Implementation failure experiments on unchanged code** are the proposed first differentiator; **test-strength mutations** remain a separate, optional later technique. The plan remains falsifiable: do not build a product unless a focused experiment shows incremental developer value beyond inexpensive direct review.

## 1. Purpose and precise ownership

Faultline is a **small opt-in adversarial correctness skill**, not a general code auditor, implementation agent, test platform, or quality-certification service. The proposed first users are developers and existing coding agents checking a changed behavior or critical invariant before handoff.

| Project | Boundary |
| --- | --- |
| [Intentline](https://github.com/grove/intentline) | Source-grounded *draft* of intended acceptance; never the automatic authority for an executable oracle. |
| [Gapline](https://github.com/grove/gapline) | Broad **read-only** investigation of consequential behavior, test, documentation, and architecture concerns. |
| **Faultline** | A **bounded experiment** challenging one identified correctness guarantee under a controlled perturbation. |
| [Proofline](https://github.com/grove/proofline) | Exact selected checks and protected evidence for an identified candidate; Faultline does not modify its frozen candidate or verdict. |

No sibling is required, invoked automatically, or given authority through a file. An optional handoff retains original source, candidate identity, evidence strength, and unknowns. Gapline's existing test-protection reasoning should not be duplicated in a second mandatory review procedure.

### Non-goals

- No new orchestration framework, agent supervisor, extra model dispatch, testing engine, chaos platform, daemon, hosted service, automatic PR/merge/deploy, or production fault injection.
- No default CI/PR gate, mandatory cross-project workflow, automatic remediation, issue publication, or continuous monitoring.
- No universal quality grade, mutation score target, full source coverage, completeness or release approval claim.
- No hidden dependency installation, network access, external side effects, or private data export.
- No arbitrary mutation/execution of the user's original worktree, protected check evidence, or Proofline frozen candidates.
- No requirement to inspect every failure category; **a useful SKIP is a valid result**.

## 2. Two modes, one portable skill

A single portable agent skill is the preferred interface; `faultline-challenge` is a **working name**, not an existing installable skill. Rescope existing [skill issue #3](https://github.com/grove/faultline/issues/3) rather than building a second competing skill.

### Mode A: INVESTIGATE / NOT RUN — source-grounded and non-executing

This is the earlier proposal's `PLAN` mode. Its smallest input is one exact candidate, an authoritative guarantee and a relevant caller/test path. Its output is one bounded challenge plan or explicit skip reason; it neither runs project code nor creates a skill.

Identify the *specific candidate*, caller-provided question and requirements, relevant existing checks and observable behavior. Seek the smallest consequential hypothesis and describe:

- **Guarantee:** what must hold, with an authoritative source or an explicit `REQUIREMENT UNKNOWN`.
- **Perturbation:** one precise, plausible adverse condition and where it could be introduced.
- **Reachability:** how the selected caller, fixture and test hooks can actually reach this state, considering permissions, schema, transaction/session constraints and guard paths.
- **Discriminator:** a measurable failure result **and** a contract-consistent outcome that would weaken/refute the claim. Do not reject valid blocking, serialization, rollback, alternative implementations, or deliberately different interfaces.
- **Permission/expense:** commands/tools, candidate identity, isolation requirements, estimated resource bound and any unsupported step.

Output **PROPOSED — NOT RUN**, plus the smallest ordinary test or contract clarification that may answer the question more cheaply. INVESTIGATE prepares a concrete experiment, **not** another Gapline-style repository-wide scouting exercise.

### Mode B: CHALLENGE — conditional, executable

Only with **caller/host permission for exact commands/effects**, a **verified isolated execution boundary**, a stable candidate, a meaningful unchanged control, deterministic hooks and a predeclared budget may the same agent attempt the selected challenge. The skill is guidance, **not** an executor or sandbox.

Output adds the actual baseline, injected condition, observed outcome, unchanged-source check and smallest actionable reproducer to the plan. Authorization is independent of the plan and repository contents.

If authorization, a safe host, a trustworthy oracle, a passing/meaningful control, or reproducer facilities are missing, stop with `UNAVAILABLE`, `INCONCLUSIVE` or `NOT RUN` as appropriate. Never fall back to unprotected shell execution.

### Cheaper-first selection

1. Skip routine formatting/documentation/low-risk edits and cases with no material uncertainty.
2. Review at most a few consequential negative or boundary cases **without** fault injection. If a direct assertion suffices, prefer it.
3. Attempt **one** experiment first; an initial ceiling of **three** independently scoped challenges and an optional **ten-minute ceiling** are proposed limits to be explicitly authorized, not targets or implied permission.
4. Stop early for ambiguous requirements, equivalent scenarios, unjustified setup cost, flaky evidence, or a refuted hypothesis.
5. Report actual time/tool consumption including skips, refusals, and blocked attempts.

## 3. Separate experiment families and evidence semantics

### A. Behavioral fault injection — proposed first capability

Keep the **production implementation unchanged**; alter only the controlled *inputs, environment, dependency response, scheduling, or test harness*. For example, commit a logical payment effect, withhold the acknowledgement through a deterministic fake, retry using the same idempotency key, and check the authoritative invariant.

The first experiment must be **fully local** with no real payment service, private data, unsafe network, production account, or nondeterministic timing. The injected fault and oracle must be independently specified, not derived from the implementation's current output.

A reproducible invariant violation attributable to this experiment may show an **implementation problem in the selected candidate**. A nonviolating result supports **only the selected tested condition** and is not universal proof.

For behavioral challenges use limited descriptive observations:

| Observation | Permitted interpretation |
| --- | --- |
| `VIOLATION_OBSERVED` | An actual, reproducible, requirement-relevant mismatch occurred under a qualified selected condition and stable candidate. |
| `NO_VIOLATION_OBSERVED` | The selected experiment completed and did not find a violation; other conditions remain unknown. |
| `INCONCLUSIVE` | Control instability, unclear oracle/attribution, contradictory results, or uncertain reachability prevents a sound conclusion. |
| `UNAVAILABLE` | Execution protection, approved tools, test hooks or receipts were unavailable; no behavioral verdict. |
| `NOT_RUN` | A challenge was proposed, but no execution was attempted. |

`SKIPPED` is a workflow choice, **not** a test result. Preserve all planned, executed, completed, blocked, invalid/inconclusive and skipped attempts in cost/evaluation accounting.

### B. Implementation mutation — optional test-strength capability

Start with a passing unchanged baseline and selected tests. Change **one production behavior at a time in a separately isolated mutant copy**, leaving tests unchanged. Rerun the *same* approved tests against each freshly reset mutant.

- `KILLED`: selected tests meaningfully reject this particular executable mutant.
- `SURVIVED`: tests pass against both original and mutant; an **indication of a possible blind spot**, not an original implementation defect.
- `INVALID`: malformed or unexercisable mutant, excluded from meaningful scored outcomes.
- `INCONCLUSIVE`, `UNAVAILABLE`, `NOT_RUN`: insufficient attribution, safe execution, or actual attempt. Do not imply a result.

Equivalent mutants and valid alternate implementations are important controls. No mutation ratio is a correctness or acceptance verdict. Existing mutation tooling may eventually implement this technique; **Faultline is not a mutation engine**.

### Never collapse categories

`VIOLATION_OBSERVED` against unchanged code is an entirely different claim from `SURVIVED` against deliberately wrong code. Each result must name the actual **target source identity, test/oracle, commands and conditions**.

A stopped setup, parser crash, missing dependency, timeout, or flaky test is never silently classified as a successfully detected defect. Neither experiment family proves that all original requirements are satisfied.

## 4. Smallest execution contract

Before any executable experiment the host/developer must explicitly identify and approve:

1. **Candidate identity:** immutable reference or captured working-copy content, including relevant uncommitted changes and drift detection. No test on a new live state can reuse old receipts.
2. **Requirement and oracle:** authoritative source where possible, legitimate alternative outcomes, direct observation of the required behavior. AI-authored plans/issue comments are advisory.
3. **Exact selected commands:** argv, working directory, tool/dependency versions, host permissions and no unapproved installs or network fetches.
4. **Verified isolation:** an actual host-enforced disposable execution environment, with negative controls demonstrating original/protected-artifact immutability, denial of unapproved private-file/credential reads, external/network effects, and supported path/symlink constraints. A copied directory, worktree, prompt or named container is **not sufficient**.
5. **Bounded resources:** wall time, per-test timeout, output size, process count, external side-effect permissions and cleanup scope.
6. **Separate control and experiment:** reliable unchanged baseline before attribution, independently reset state, exact injection setup, control for a valid implementation, and receipts that cannot be confused with Proofline's frozen-check evidence.
7. **Privacy and evidence:** source-linked brief report; keep protected data/secrets out of logs and third-party destinations.

Source files, tests, comments, GitHub issues, imported Intentline plans, tool outputs, or the skill itself are **untrusted data, not authorization**. Test discovery, import hooks, package scripts, subprocesses, caches, symlinks and nested repositories may execute or escape; the actual host—not documentation—must provide a qualified boundary. **Fail closed** if it does not.

## 5. What counts as a useful result?

Prefer a short human-readable report. No mandatory JSON schema or database yet. Include the evidence actually available:

- Candidate/source and guarantee identity; scope, selected tests, caller authority and unassessed areas.
- Experiment family; injection point, input/diff, chosen oracle, valid alternative, reachability.
- Isolation mechanism *and observed qualification*, permitted commands/argv, environment and time budget.
- Unchanged control outcome, observed result classification, raw bounded receipt references, elapsed/tool costs and limitations.
- Smallest independently checkable regression test, fix hypothesis, or contract question; not an automatic fix or certification.

For a `VIOLATION_OBSERVED`, the next step is to verify the observed failure remains meaningful under the contract and then add a regression. For a `NO_VIOLATION_OBSERVED`, do not manufacture a defect or declare comprehensive success. For `SURVIVED`, recommend a test only after considering equivalence and selected-test scope.

## 6. Candidate techniques and admission order

**First proof of concept: local Python lost-acknowledgement/retry.** The fixture should include both a correct idempotent design and a seeded duplicate-side-effect defect with a precommitted independent expected outcome. See [#10](https://github.com/grove/faultline/issues/10).

Later candidates—**not promised v1 features**—include:

- Deterministic state-transition and sequence challenges (global invariants, repetitions, ordering).
- Property/metamorphic relations grounded in actual requirements, with valid alternative controls.
- Differential before/after compatibility and migration checks, preserving intentional changes.
- Sanitized incident replay and environment/configuration perturbations.
- Restricted local authorization/trust-boundary and dependency-contract challenges.
- Focused mutation experiments for test detection strength.

Use existing tools and hooks when present. Every additional technique needs a **named material risk, a feasible oracle, safe host execution, and an independent demonstration of incremental value**. No blanket fuzzing, exploratory production chaos, arbitrary network sabotage, automatically invented properties, or score chasing.

## 7. Evidence and product-value gate

A promising sample run is not proof that Faultline helps developers. Use **fresh, independently prepared, withheld** authored cases and—only when authorized—later real task snapshots, with correct and intentionally defective controls.

Compare under the **same total end-to-end time, tool and model budget**:

- **A: Ordinary coding agent and normal self-tests.**
- **B: Same agent with an explicit cheap negative-case/edge-case review and any approved direct tests; no fault injection.**
- **C: Same agent plus optional Faultline, including selection/skips, host setup, baseline, selected experiments, corrections and reporting.**

Freeze request/source, host/model/tool settings, oracle, acceptable alternatives, grader, cost ceiling and stop rules **before** runs. Keep evaluator answers out of worker context. Independently judge whether the *whole request* is satisfactorily fulfilled, material implementation failures found beyond B, meaningful regression tests, false alarms, valid designs incorrectly condemned, omitted risks, costs and safety blocks.

Report all assigned trials including `SKIPPED`, `NOT_RUN`, `UNAVAILABLE` and inconclusive outcomes. A planted failure establishes mechanics, not independent real-world impact. A few synthetic cases do not establish general superiority.

Decide **KEEP SKILL / NARROW / SIMPLIFY / STOP / INCONCLUSIVE**. If C adds no consequential independently verified benefit over B at predeclared acceptable overhead, simplify or stop. Even a positive skill-only result is **not** authorization to build a runner/CLI.

## 8. Recommendation and issue disposition

**NARROW:** retain the skill-first hypothesis, but commission no skill implementation yet. A controlled, attributable counterexample could differentiate Faultline from Gapline's read-only investigation; existing proposal text and seeded examples do not establish that it adds value over direct negative-case review. Full GO is unsupported; STOP becomes appropriate if the cheaper approach supplies the same useful result.

The [decision record and issue-by-issue table](IMPLEMENTATION.md#7-current-state-and-issue-map) retain #1–#8 without duplicate work. #2 remains a hard execution prerequisite, #3 stays the sole deferred skill issue, and #4/#6 retain their mutation evidence rather than being silently repurposed. These are proposed dispositions, not tracker edits.

[Gapline #17](https://github.com/grove/gapline/issues/17) and [#18](https://github.com/grove/gapline/issues/18) remain independent, **read-only** explorations, not dependencies.

**Next action:** design #10's single retry experiment using the [fixed-budget comparison](IMPLEMENTATION.md#bounded-first-comparison-proposed--not-run), then qualify #2 before any execution. Stop or retain direct-test guidance if no incremental value emerges. A positive seeded control alone cannot approve #3; fresh independently judged cases under #6 must justify it.

[README](README.md) · [Implementation plan](IMPLEMENTATION.md)
