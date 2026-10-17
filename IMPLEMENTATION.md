# Faultline — implementation plan

**Status:** Proposed; no audit implementation exists yet.  
**First release target:** one useful, safe, optional `faultline-audit` agent skill for small Python changes.  
**Admission rule:** a runtime/CLI is **not** in scope unless a bounded evaluation shows the skill is useful and identifies an execution problem worth solving.

Read [README.md](README.md) for the public introduction and [DESIGN.md](DESIGN.md) for the governing scope, trust boundaries, and observation definitions.

## 0. Product decision and starting state

The first job is **not to build a comprehensive quality platform**. It is to find out whether a small, repeatable test-strength audit finds defects ordinary agents miss at a worthwhile cost.

Existing options already provide mutation engines, coverage collection, complexity analysis, and clone detection. Prefer using properly installed tools over replacing them. CRAP and DRY are optional prioritization hints; **mutation experiments with meaningful, verified outcomes are the core**.

The repository initially contains only the Apache-2.0 license and these three documents. There is no working installation procedure, CLI, test runner, benchmark result, completed skill, integration, or published release. No future milestone below should be described as complete until verified.

### Default constraints for all milestones

- Python 3.11+ for authored reference fixtures and simple offline development tests; **no required Faultline runtime dependency** in the first release.
- The skill runs within an existing user's coding agent; no extra model, runner, network installer, or online account is required by Faultline.
- Actual mutation test commands need explicit host/user authorization and a **verified isolated execution boundary**. A copied directory alone is insufficient. If unavailable, **do not run mutations**.
- Keep original candidate, private inputs, tests, and any Proofline snapshots untouched. Generated disposable mutant copies are separate from audit records.
- Baseline must pass on the same selected test commands before comparing mutations. Do not infer killed/survived from failing, incomplete, or flaky baselines.
- Preserve negative results, refusals, unknowns, and time spent. Never call a green suite or a high mutation score complete proof.
- Avoid creating an obligatory stage in Intentline or Proofline.

## 1. Milestone A — make one small skill usable

**Deliverables**

- `faultline-audit/SKILL.md` — the **single canonical portable root-level skill**. Start with minimal frontmatter (`name: faultline-audit` and an accurate description) and simple direct-file instructions for hosts that do not auto-discover skills.
- README update with a **verified** skill installation or manual invocation example (not before actually testing it).
- `tests/test_skill.py` or a similarly small standard-library regression test for skill discoverability, required safety language, and link/path validity. Tests of text alone are **not** proof of safe agent execution.

**Required skill behavior**

1. Ask/confirm target, selected authorized commands, allowable scope, isolation method, resource budget, and intended output. Do not ask for an unnecessary acceptance ceremony.
2. Default to a small experiment: propose **at most three mutations and a ten-minute audit budget** for caller confirmation; never silently infer approval or enlarge the budget.
3. Read the changed code and existing tests. If complexity/coverage tools are installed, use their output as explicitly scoped advisory prioritization; do not install anything automatically.
4. Verify isolated disposable workspace before executing any baseline or mutated check. If this is impossible, explain the blocker and offer only a **non-executing** audit plan.
5. Capture a reproducible pristine candidate identity and approved command list; run unchanged baseline.
6. Select a few plausible, requirement-relevant mutations, one per fresh/reset mutant copy, keeping test code fixed; record exact diffs.
7. Classify observed results using the states in [DESIGN.md](DESIGN.md), including `INVALID`, `INCONCLUSIVE`, `UNAVAILABLE`, and `NOT_RUN`. Keep all denominators.
8. Return a short report focused on the most material survivor and smallest relevant additional assertion, including why it might be equivalent or unexercised.

**Acceptance tests**

- The instructions do not authorize themselves to run commands, install dependencies, write to the original source, or publish code.
- Every proposed mutation is attributable to a named candidate/test scope; no global correctness grades.
- Baseline fail, timeout, lack of sandbox, tool unavailable, malformed mutant, suspected equivalent, and exhausted budget each receive an honest result.
- Agent can perform an **entirely read-only** review when execution is not authorized.
- The skill adds no dependencies or behavior changes to Intentline or Proofline.

**Stop if:** the skill cannot distinguish a safe, bounded executable audit from advice-only analysis. Fix that first; do not add more features.

## 2. Milestone B — qualify mechanics with authored controls

Use tiny public Python fixtures under `tests/fixtures/` (or `evaluation/fixtures/` if a separate experiment corpus is warranted). Keep them independently editable without altering the original repo during a run.

Minimum controls, each with an explicit expected observation:

| Control | Baseline and mutation | Expected behavior |
| --- | --- | --- |
| Detectable boundary defect | Passing baseline; change a threshold where a targeted assertion exists | `KILLED` and a named observed failing test |
| Green-suite blind spot | Passing baseline; change an untested edge while selected tests remain green | `SURVIVED`, actionable test suggestion, **not** a claim the original is wrong |
| Alternate valid implementation | Different correct implementation for the same contract | Avoid a false correctness or duplication failure; discuss behavior, not syntax alone |
| Invalid mutation | Introduce a mutation causing invalid syntax or unsupported execution | `INVALID`, excluded from meaningful killed/survived denominator |
| Failing/flaky baseline | Tests are already failing or observably unstable | Refuse meaningful mutation verdict; `INCONCLUSIVE`/`UNAVAILABLE` |
| Missing execution protection | Isolation negative canary cannot establish required separation | `UNAVAILABLE`; no unsafe fallback |
| Timeout or missing tool | No meaningful execution receipt | `UNAVAILABLE` with consumed budget preserved |
| Changed candidate mid-audit | Original candidate identity no longer matches scope | Treat older evidence as stale; restart or report `INCONCLUSIVE` |

**Execution qualification** is essential: on the actual intended host, run disposable **negative controls** showing that a test process cannot modify the original candidate or protected report location, read private sentinel files, or perform unwanted network effects. Record precisely what was observed and what remains unqualified. If the host cannot enforce those boundaries, mutation execution is **NO-GO**; fixture expectations must not be passed off as actual protection.

Do not commit secrets, private requests, uncontrolled test receipts, or any external source captures.

**Acceptance:** a fresh qualified host run produces accurate classifications for the controls and retains the complete candidate/mutant/test identity. Expected fixture labels do not themselves constitute observed outcomes. Python unit tests and skill instructions are necessary, but not sufficient, to establish the host security boundary.

## 3. Milestone C — focused dogfooding

Only after Milestone B execution controls qualify, test the skill against real, approved candidate snapshots, with clearly bounded commands. Good initial targets are:

- [Proofline: `checks/promise_evidence.py`](https://github.com/grove/proofline/blob/main/checks/promise_evidence.py) and its tests: R-to-check attribution and `NOT DEMONSTRATED` versus linked passing checks.
- [Proofline: `checks/intentline_advisory.py`](https://github.com/grove/proofline/blob/main/checks/intentline_advisory.py) and its tests: source identity, canonical JSON, and export tampering.
- [Intentline: `intentline/contracts.py`](https://github.com/grove/intentline/blob/main/intentline/contracts.py) and its tests: exact source citation validation and contract records.
- [Intentline: `intentline/continuity.py`](https://github.com/grove/intentline/blob/main/intentline/continuity.py) and its tests: changed obligations, lineage, and adoption boundary semantics.

Treat these as **candidate audit targets**, not as known defects. Obtain permission for exact commands and disposable host runs. Their tests already contain substantial negative coverage; finding no substantive survivor may be a valid outcome.

For each audit, retain a compact case note:

```text
Original candidate/ref:
Selected source behavior:
Selected tests and exact argv:
Isolation and boundary evidence:
Approved time/mutation budget:
Baseline: PASSED / FAILED / UNAVAILABLE / INCONCLUSIVE
Mutations: proposed / executed / killed / survived / invalid / inconclusive / unavailable / not-run
Material gap with exact observation (if any):
New test suggested and later independently run? YES / NO / NOT OBSERVED
Time/tool overhead:
Known omissions and other unassessed behavior:
```

**Acceptance:** at least one complete evidence packet (including an honest no-findings result if applicable), with stable identities and no mutation of original projects.

**Stop/adjust if:** command setup or report overhead overwhelms a few controlled mutations, the skill repeatedly proposes trivial/equivalent mutants, or isolation cannot be demonstrated.

## 4. Milestone D — measure actual added value

Dogfooding is not evidence that Faultline helps coding agents generally. Conduct a **small, predeclared matched evaluation** only after the mechanics are reproducible and there is explicit authorization for any model/tool expenditures.

### Before any worker attempt

- Select **four to six fresh realistic Python tasks**, with real negative/compatibility boundaries and an ordinary low-risk control. Do not train or repeatedly optimize on the evaluation cases.
- Freeze source requests, exact base commits, tests, tool and host versions, permitted commands, candidate access, mutation/time budgets, model/agent settings, and stop rules.
- Prepare **independently authored and withheld** behavioral oracles and valid-alternative/defective controls. Qualify the grader before showing a worker the task. Never claim an authored mutation is automatically a real missed user obligation.
- Ensure external model spend, source permission, and environment isolation are authorized; record unavailable data as `UNKNOWN`.

### Two arms; no extra ceremony

| Arm | Actual workflow |
| --- | --- |
| **A. Ordinary** | Existing coding agent uses its normal tests and self-checking. |
| **B. Ordinary + optional Faultline skill** | Same agent, base, allowed tools, and total task budget, with the skill permitted after coding. Count all mutation setup/check time and model/tool usage. |

Run from separate fresh snapshots. Prevent later attempts from seeing earlier solutions or private graders. Never change arms/tasks after seeing a favorable result without declaring a new cohort.

**Primary outcome:** independently satisfactory complete delivery across *all assigned tasks*, not mutation score or number of new tests.

**Secondary outcomes:** independently confirmed previously undetected defects found; tests added that kill material negative controls; false alarms/equivalent-mutant distraction; false acceptance; correct-but-blocked handoffs; unfinished or unavailable episodes; end-to-end elapsed time, tooling overhead and model usage where observable.

**Predeclared ceiling stop:** if ordinary A already delivers every task correctly and no meaningful test weakness is independently confirmed, stop rather than pretending the extra workflow proves itself. Retain all unfinished B assignments as `NOT_RUN` and report **INCONCLUSIVE**.

**Decision:** choose `KEEP SKILL`, `SIMPLIFY`, `OPTIONAL`, or `STOP` using independently graded improvements **and** overhead. A small study cannot justify universal mandatory adoption. A promising discovery should be checked again on unseen holdout tasks before product claims.

## 5. Milestone E — conditional CLI, only after a positive decision

**Not committed work.** Build only if the previous milestones demonstrate a specific mechanical failure of skill-only operation: for example, non-reproducible mutant reset, unstructured receipts, unsafe mutation scope, or report identity drift that a small local tool would solve.

If a CLI is admitted, the **smallest** reasonable interface is a local, opt-in audit against an explicitly authorized candidate and existing tests, with bounded mutations and concise receipts. Before defining flags or a public schema, require:

- Exact original/candidate/mutant identities and immutable or separately stored test observations.
- Host-qualified execution isolation, no unsafe fallback, no original worktree writes.
- One mutation per isolated reset state, stable approved command argv, finite budget and explicit tool/environment provenance.
- Distinct observations for killed/survived/invalid/inconclusive/unavailable/not-run; invalid/suspected-equivalent cases cannot inflate a score.
- Evidence review without needing Intentline/Proofline, model accounts, network, or publishing permission.
- A measured benefit versus the skill using existing tools, not merely attractive architecture.

If the skill is enough, **never build this CLI**. No new runtime does not mean project failure.

## 6. Minimum project structure

**Now (documentation stage)**

```text
faultline/
  LICENSE
  README.md
  DESIGN.md
  IMPLEMENTATION.md
```

**After Milestone A, only when verified**

```text
faultline/
  faultline-audit/
    SKILL.md
  tests/
    test_skill.py
```

**After Milestone B, only as needed**

```text
  tests/
    fixtures/
      ...
```

Keep one canonical skill file. Avoid duplicated installed-skill copies, an upfront Python package, speculative config, benchmark machinery, or a fixed report schema.

## 7. Practical acceptance checklist for the first usable version

- [ ] One discoverable portable skill with honest status and direct-file usage.
- [ ] No additional inference dispatch or external service requirement.
- [ ] Explicit caller-authorized commands, budget, and actual isolated execution controls.
- [ ] Original source and tests unchanged; one reset disposable copy per mutation.
- [ ] Baseline before mutations; failing/unavailable baseline never yields a success score.
- [ ] At least one observed `KILLED`, one `SURVIVED`, and one intentionally unavailable/inconclusive control in qualified disposable fixtures.
- [ ] Mutation results retain source/test/candidate identity and all outcomes, not just favorable ones.
- [ ] One concise report with a reproducible surviving-mutant counterexample and an actionable next test.
- [ ] README install/use instructions verified on an actual supported host.
- [ ] Honest limitations and explicit **no correctness certification** language throughout.

## 8. Work ordering and stop rule

Suggested sequence: **docs → canonical skill → authored fixtures + isolation qualification → small approved dogfood audits → independently graded usefulness comparison → conditional decision**.

Do not open feature branches for a general CLI, integrations, automatic test writing, CI enforcement, code duplication refactoring, or multi-language mutation until there is evidence of a specific need. Quality-of-evidence improvements are welcome; feature count is not a success metric.

**First next task:** implement only Milestone A, then demonstrate the Milestone B isolation gate and controls *before* claiming an executable mutation audit.
