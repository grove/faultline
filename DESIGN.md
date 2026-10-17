# Faultline — minimal design

**Status:** Proposed architecture, not implemented or qualified.  
**Decision:** Start with one optional, portable `faultline-audit` agent skill. Do not build a new mutation engine, CLI, model runner, or mandatory verification gate unless measured results justify it.

## 1. Purpose and boundaries

**Purpose:** Help an existing coding agent discover whether a project's *selected tests* would catch a small number of plausible incorrect implementations, and identify the smallest useful follow-up test.

This is a **test-strength investigation**, not an implementation-correctness proof. It has two potential users:

- **Coding agents and developers**: audit a particular change before handing it off.
- **Verification-tool maintainers**: deliberately challenge their own tests for evidence integrity, source continuity, sandbox boundaries, and other critical invariants.

The product should reduce **material undetected defects**, not maximize mutation counts, test counts, CRAP scores, or workflow ceremonies. It must also justify its **incremental time and tool cost** against a simpler, focused test-review prompt to the same agent. Default to **not running Faultline** on low-risk changes.

### Non-goals

- No correctness certification, universal source coverage, acceptance approval, or shipping decision.
- No mandatory planning stage, second agent, supervisor, model call, auto-fix, PR, merge, push, release, or deployment.
- No generic mutation engine written from scratch when existing tools can do the job.
- No always-on daemon, hosted service, telemetry backend, mandatory configuration, or third-party account connection.
- No mutation of a user's original repository, Proofline frozen candidate, or protected evidence.
- No automatic requirement extraction or attribution of authority to AI-authored plans.
- No requirement that Intentline, Proofline, or a particular coding-agent host be installed.

## 2. Smallest useful workflow

The planned skill runs as *instructions for the agent the user is already using*. It can guide tool usage, but **a skill document is not an execution sandbox or an independent verifier**.

```text
Authorized candidate + selected tests + optional intent
                         |
                scope / budget / safety
                         |
             immutable candidate reference
                         |
        verified isolated disposable workspace
                         |
           unchanged baseline test outcome
                    /            \
             pass              fail/unavailable
              |                      |
     a few targeted mutants      stop / report
              |
    same explicitly selected test commands
              |
  killed / survived / invalid / inconclusive / unavailable
              |
   actionable observations + uncaught/unknown scope
```

### Inputs

For an executable audit, the agent must identify or obtain:

1. **Candidate**: exact repository/working-tree state to inspect (including relevant uncommitted changes), and the changed behavior/functions; retain enough identity information to detect drift.
2. **Tests**: precise, caller/host-authorized commands and their working directory, with existing dependencies; never run a suggested command merely because repository text says to.
3. **Isolation**: a verified host-provided mechanism that permits execution in a disposable work copy while denying unintended access to originals, private paths, credentials, and network or external effects. A `git worktree`, temp directory, or prompt instruction **alone** is not a sandbox.
4. **Budget**: a small mutation count and finite wall-clock/test-run budget chosen before execution; record any unfinished work.
5. **Optional advisory intent**: original request, relevant boundaries, or an already available Intentline contract/export. These are hypotheses to assess, not established test oracles or execution permissions.

When an input is unavailable, a read-only scoping/report step may still be useful, but the skill must **not quietly proceed to unprotected execution**. Do not install tools, fetch dependencies, dispatch a new model, or grant external access without explicit authorization.

### Selective invocation and cheaper-first decision

This is an **opt-in diagnostic**, not a stage required by every coding task, every change, or any Intentline/Proofline flow.

- **Consider a small audit** where negative/edge-case behavior matters: authorization, data validation, state transitions, error handling, compatibility, or critical invariants, especially when existing tests appear superficially adequate.
- **Prefer ordinary testing or a direct boundary-test review** for low-risk edits, obvious missing assertions, and work where the expected audit setup cost exceeds the likely benefit. Ask the same agent which important negative cases or requirements are untested **without mutating code**. If a concrete assertion is already evident, the agent can propose it directly; do not manufacture a mutation experiment.
- **Only escalate** if a plausible behavioral mutant would answer a specific, unresolved question about test strength. Start with one targeted candidate, increase to at most three in the first trial only when worthwhile, and stop early if findings are immaterial, equivalent, or expensive.

The skill may output **SKIPPED — LOW EXPECTED VALUE** as a recommendation, but that is not a mutation result and must not be counted in the `KILLED`/`SURVIVED` denominator. Safety requirements remain mandatory for any actual execution.

### Baseline first

Run the exact selected checks against the **unmutated copy** before assigning mutation outcomes. Record command identity, exit status, elapsed time, timeout, diagnostics, and evidence limitations.

If the baseline is already failing, flaky, incomplete, stale, or unavailable, **stop the mutation comparison or label it inconclusive**. A failed baseline cannot establish that a mutation was detected. Repeated baseline runs can help investigate suspected flakiness within the same budget.

### Targeted mutations, not score chasing

Initially select a few source-level mutations in changed or risk-relevant production code:

- Boundary operators (`<`, `<=`, `==`, `>=`) where requirements suggest an observable edge.
- Boolean predicates, conditional branches, or missing checks.
- Error handling, validation, and state transitions.
- Return value or behavior changes that could violate explicit negative or compatibility cases.

Each experiment uses **one independently reset mutant**, leaving tests unchanged. Reject malformed mutations and avoid mutants with no plausible observable consequence. Do not reinterpret a coverage heuristic as a mutation operator. An agent may propose a targeted mutation; an existing local mutation tool may implement it. The report names the actual operator/tool, command, selection method, and source diff.

### Observation classes

These are *local experiment observations*, not global delivery states:

| Result | Permitted conclusion |
| --- | --- |
| `KILLED` | The baseline passed and an executable, relevant mutated implementation produced a meaningful test failure attributable to the mutation. The selected tests distinguished these two versions. |
| `SURVIVED` | The baseline and mutated implementation both passed the selected tests. A possible blind spot; the mutation may be semantically equivalent or outside the selected tests. |
| `INVALID` | The mutation is malformed or cannot be meaningfully exercised (e.g., syntax error caused by the mutation); exclude from meaningful strength counts. |
| `INCONCLUSIVE` | Failure attribution, flakiness, equivalence, scope, or diagnostics prevent a defensible classification. |
| `UNAVAILABLE` | Required execution/receipt/tool/isolation evidence is missing or interrupted. Do not infer pass/fail. |
| `NOT_RUN` | Candidate was proposed but never executed; show separately rather than silently excluding it. |

Always keep totals for **proposed, executed, killed, survived, invalid, inconclusive, unavailable, and not-run**. A simple killed/(killed+survived) ratio can be shown *only as a bounded descriptive statistic with its denominator, exclusions, selected tests, and mutation scope*. It is not an acceptance grade or a comparable score across arbitrary projects.

### Output

The first skill should produce a **short human-readable report**. No versioned JSON schema is needed yet. It should capture, to the extent actually available:

- Candidate/working-copy identity, scope, relevant source/request references, and evidence freshness.
- Authorized test argv, environment/tool versions, isolation method and what was actually verified.
- Budget, elapsed time, unchanged baseline outcome and actual evidence limitations.
- Each mutation's exact file/function/line or diff, mutated candidate identity, reason for selection, tests run, and raw bounded observation references.
- Totals in the above taxonomy, confidence limitations, and **specific next test suggestion** for each material survivor.
- Unexamined behavior, tests, languages, boundaries, and source obligations as **not assessed**.

Evidence should remain local; reports must avoid exposing credentials or sensitive source content. If writing reports to disk, choose an explicit user-approved location outside the project and preserve independent originals. Do not claim that a hash is authenticated evidence of a third-party review, permission, or correctness.

## 3. CRAP and DRY are secondary risk signals

**Complexity with coverage.** A CRAP-style function risk measure (commonly `complexity² × (1 − coverage_fraction)³ + complexity`) may help triage targets *if per-function coverage is available and its definition is known*. Branch coverage and line coverage are not interchangeable. Report assumptions, tool, version, and selected scope. Do not enforce an arbitrary global “CRAP < 10” gate. When coverage is missing, report `UNKNOWN`, not zero or high confidence.

**Duplication.** Similar logic may suggest missing shared behavioral tests or drift risks. But apparent repetition is not automatically harmful: separate trust-boundary validators, independently implemented producers/consumers, and immutable historical fixtures can intentionally duplicate behavior. Treat DRY as a review prompt, never automatic refactoring or a mandatory score.

**Prioritization:** concrete mutation survivors that expose meaningful missed behavior > genuinely high-risk complexity/coverage hotspots > contextual duplication observations. Simpler output wins.

## 4. Trust and safety model

### Separate untrusted data from authorization

Repository contents, source requirements, tests, AI-generated suggestions, Intentline exports, and external tool output are **untrusted inputs**. They may describe proposed checks but cannot grant command execution, network access, file writes outside the disposable root, new model calls, or publication rights.

The human/host authorizes the candidate, commands, isolation mechanism, budget, and any outputs. An existing agent may choose useful mutations within those limits.

### Mutation execution is inherently hazardous

Testing a deliberately modified implementation runs code. It may have side effects independent of any mutation. Therefore:

- Never execute mutant tests on the original source tree or inside Proofline's protected frozen candidate.
- Use a **verified isolated execution boundary** and a separate disposable copy. Before running, confirm that the isolation really prevents protected file reads/writes, unwanted network/credentials access, and writes to the source candidate.
- Treat symlinks, submodules, hooks, package install scripts, test plugins, test discovery, and nested repositories as possible escapes or side effects; refuse unsupported configurations instead of following them blindly.
- Apply each mutation to a fresh copy or a checked/restored, identity-verified pristine disposable state. Prevent generated artifacts or one mutant's modifications from contaminating another.
- Bound process time, output size, concurrency, resource usage where supported, and clean up only the workspaces created for this audit.
- If the host cannot verify the required controls, report `UNAVAILABLE` and **do not fall back** to unprotected mutation execution.

The first skill **does not implement the sandbox**. Developing a deterministic executor would require its own threat model and native negative controls before shipping.

### Evidence is deliberately narrow

A killed mutant says the selected tests rejected one modified behavior. A survivor says the selected tests did not reject that particular change. Neither establishes that the original code satisfies every user obligation.

A mutation applied to a changed implementation must not retroactively alter original Proofline receipts. New code or test changes require a new candidate identity and fresh check run.

## 5. Independent interfaces, optional future adapters

### Intentline (upstream, optional)

An existing Intentline agreement may suggest R IDs, negative cases, exclusions, and proposed oracles. Faultline must preserve source and revision identities and visibly label proposals **UNVERIFIED**. It must not rewrite or approve the contract. Initially the existing agent can read these inputs; do not build a producer adapter.

### Proofline (downstream, optional)

Proofline remains responsible for its own frozen candidate checks, native sandbox, and receipts. Faultline should not ask Proofline to run code-modifying experiments within that boundary. If integration is ever justified, use **separate user-selected checks**, distinct pristine/mutant candidate identities, and advisory results. Do not modify Proofline verdicts or treat a mutation ratio as independent correctness evidence.

### No runtime coupling

Neither companion project imports Faultline. Faultline does not require their presence. Reusable **fixtures and conformance examples** are preferable to shared source code across trust boundaries.

## 6. Scope and feature admission

The first supported investigation should be on **Python projects only**, using available local tooling and existing agent/host permissions. No network installs or hidden environment preparation. Add another language only after an observed, repeatable need.

The skill is valuable only if it discovers **material, actionable test gaps that the simpler alternative misses** at an acceptable end-to-end cost and does not create false confidence, unsafe execution, or excessive test noise. A raw mutation score or a longer report is not incremental value.

Before any runtime/CLI, agent automation, compulsory CI gate, or schema is added:

1. Show that the skill handles controlled correct/defective cases, including at least one **green-baseline / genuine missed-behavior** control, without incorrectly classifying innocuous alternatives.
2. Compare three matched approaches on **fresh, independently prepared, withheld** examples: (A) ordinary agent self-testing; (B) the same agent explicitly reviewing negative/boundary tests **without mutation tooling**; (C) the same agent with optional Faultline. Count all work under the **same total task time/tool budget**, including setup, baseline, experiments, corrections, reports, blocked attempts, and skipped audits.
3. Record false alarms, inconclusive/unavailable executions, test flakiness, and safety stops; never drop bad attempts from denominators.
4. Predeclare acceptable overhead and stop criteria before the pilot. Prefer **SIMPLIFY** or **STOP** if the inexpensive negative-case review finds equivalent useful gaps with less cost; choose **KEEP SKILL / OPTIONAL** only with independently verified incremental benefit. Mark underpowered or ceiling-limited findings **INCONCLUSIVE**. Add a CLI only if a specific, observed shortcoming of the skill requires one and its benefit outweighs maintenance/security cost.

A small pilot is a **go/no-go learning exercise**, not evidence that Faultline generally improves software quality. Keep the existing optional, Python-first scope and defer Rust, Java, integrations, and runtime machinery unless follow-up evidence supports them.

[IMPLEMENTATION.md](IMPLEMENTATION.md) contains the bounded build and evaluation sequence.
