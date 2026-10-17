# Faultline

**Know what your tests might miss.**

Faultline is a proposed, opt-in **test-strength audit for existing coding agents**. Its goal is to find plausible defects that a project's current tests do not catch, and to give the agent concrete, bounded feedback for improving those tests.

The starting point is a **small standalone agent skill**, not a new agent controller, proof system, or mutation-testing engine. It will use tools already available in the developer's environment and operate only in a properly isolated, disposable work area. A separate CLI is a future option **only if measured usefulness justifies building one**.

> **Status: design only.** This repository currently contains the project documents and license, not an implemented audit skill or executable product. Nothing here implies that an audit has run, that a mutation has been tested, or that any implementation is verified.
>
> **Value is unproven.** Faultline has not yet shown that it improves independently judged delivery quality or finds material test gaps more efficiently than simply asking the coding agent to review boundary and negative cases.

[Design](DESIGN.md) · [Implementation plan](IMPLEMENTATION.md)

## Why Faultline?

A test suite can be green and still miss an important requirement:

- A boundary check changes from `>= 5` to `> 5`, but no test covers the fifth attempt.
- A validation function stops stripping whitespace, but tests cover only an empty string.
- An error is silently swallowed, but tests only exercise success.
- A complex function has high nominal coverage but weak assertions.

Mutation testing explores this gap by deliberately changing *implementation code* in a **disposable copy**, rerunning the same relevant tests, and observing whether they detect the change.

Faultline's question is deliberately narrower than “Is this code correct?”:

**Would the selected tests detect these specific, plausible incorrect behaviors?**

## When to use it — and when to skip it

Faultline is an **optional escalation for risk-relevant changes**, not a default coding step or a mandatory stage of a multi-skill workflow. It is most plausible for authorization and trust boundaries, negative validation, state transitions, error handling, compatibility obligations, and other failures that a green suite could conceal.

**Skip it** for documentation, formatting, routine mechanical changes, and low-risk work where the cost of an audit is unlikely to pay back. Before mutating code, let the *same agent* examine requirements and tests and propose a few concrete boundary/negative assertions **without mutation tooling**. If an obvious useful test can be added directly, prefer that cheaper path. Try a mutant only when it can answer a remaining material uncertainty.

Start with **one targeted mutation**, expanding only if warranted, to at most three in a first audit. Ten minutes is a **proposed maximum for explicit authorization**, not a duration target or permission to execute. Stop early when setup cost, equivalent-mutant noise, or poor evidence outweighs useful findings.

## What the first skill will do

The planned `faultline-audit` skill will guide an **already-running coding agent** through a bounded, evidence-based audit:

1. Identify the changed behavior and relevant existing tests. Use requirements supplied by the caller if available; do not invent approval or pretend completeness.
2. Confirm explicit permission for the selected test commands, a usable isolated work area, and a time/mutation budget. Stop if these are unavailable.
3. Establish an unchanged baseline: candidate identity, exact test commands, environment, and a passing baseline test run.
4. Use complexity/coverage signals to prioritize a small number of meaningful mutation candidates; duplication is a secondary review signal.
5. Introduce one controlled implementation mutation at a time **outside the original worktree**, rerun the relevant approved checks, and classify the actual observation.
6. Give concise, source-linked suggestions for additional assertions or test boundaries, preserving raw tool evidence and every unknown.

The skill itself cannot guarantee sandboxing. It must require a **verified isolation mechanism provided by the host or developer** before executing arbitrary repository test commands. Instructions alone are not a security boundary.

### Illustrative result — not an actual run

```text
Candidate: <exact working-copy identity>
Baseline: selected tests PASSED
Mutation: username validation no longer rejects whitespace-only strings
Observation: SURVIVED — the selected tests still passed
Suggested next check: assert that "   " is rejected, while valid Unicode inputs remain accepted
Confidence: limited to this mutation, these tests, and this candidate
Other source requirements: NOT ASSESSED
```

The important outcome is a reproducible *counterexample to test strength*, not a high mutation score.

## What CRAP, mutation testing, and DRY contribute

| Signal | Useful question | Important limit |
| --- | --- | --- |
| **Complexity + coverage (CRAP-style)** | Which complex, poorly covered functions deserve attention first? | Risk heuristic, not a universal quality gate. Coverage granularity/tooling must be stated. |
| **Mutation testing** | Do selected tests fail when a plausible defect is introduced? | A surviving mutant may be equivalent or untested; a killed mutant does not prove complete correctness. |
| **Duplication (DRY)** | Is repeated logic increasing the chance of inconsistent behavior or maintenance mistakes? | Deliberate independence at trust boundaries can be safer than reuse. |

Faultline is not trying to replace mature mutation, coverage, or duplication tools. It aims to **select useful questions, orchestrate a small authorized experiment, and report evidence honestly**.

## Relationship to Intentline and Proofline

All three projects can be used independently.

| Project | Responsibility |
| --- | --- |
| [Intentline](https://github.com/grove/intentline) | Capture what was requested and propose source-grounded acceptance criteria and evidence boundaries. |
| **Faultline** | Probe whether tests would detect selected plausible defects; distinguish observed test strength from unknown behavior. |
| [Proofline](https://github.com/grove/proofline) | Run expressly selected checks against a frozen candidate within its supported protected boundary, preserving native receipts. |

**No integration is required for the first skill.** If an agent already has an Intentline plan, it may use proposed boundaries and R IDs as *advisory inputs*. Those plans do not become verified test oracles.

Do **not** run a code-mutating audit inside Proofline's read-only frozen candidate. Any future interoperability must retain separate candidate/mutant identities and must never upgrade a passing check or mutation score into a delivery-acceptance verdict.

## Scope and safety

The initial target is **Python repositories**, because both companion projects are Python-based. The skill should remain conceptually language-neutral; other languages can be considered after the Python workflow works.

- **Opt-in and budgeted:** no mandatory PR gate, background service, new model dispatch, automatic repair, or automatic publication.
- **No source worktree mutation:** modifications are permitted only in an explicitly approved, disposable and isolated copy; keep the original candidate unchanged.
- **No implicit command authorization:** source files, requirements, agent output, and tool reports are untrusted data. Only the actual caller/host can authorize command execution or external effects.
- **No unsafe fallback:** if isolation, baseline checks, dependencies, or meaningful receipts are unavailable, report `NOT_RUN`/`UNAVAILABLE` rather than executing unsafely.
- **No universal correctness claim:** a pass, mutation score, complexity score, or duplicate scan is limited evidence. Unknown or unexamined requirements remain unknown.
- **No secrets in reports:** do not upload private code or captured test output to third-party services without separate authorization.

## What happens next?

Read [IMPLEMENTATION.md](IMPLEMENTATION.md) for the staged work: qualify one small `faultline-audit` skill, test its mechanics on controlled Python examples, and compare **ordinary agent self-testing**, **focused boundary-test review without mutations**, and **optional Faultline** on fresh tasks under the same end-to-end time/tool budget. Measure independently verified missed behavior, final task correctness, noise, and total overhead. **If Faultline cannot beat the simpler review at an acceptable cost, simplify or stop** rather than building a CLI or another process.

There is **no install command yet**. When the skill exists, this README will be updated with a verified installation and first-use walkthrough, not a speculative command.

## License

Apache-2.0; see [LICENSE](LICENSE).
