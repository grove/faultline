# Faultline

**Find the important failures your tests might miss.**

Faultline helps your existing coding agent identify important promises in your
code, challenge how they could fail, and check whether your tests would notice.
It explains realistic consequences and suggests the smallest useful regression
test. Audit works without Docker, dependencies, infrastructure setup, or running
your project's code.

## 1. Install the skill

Open a terminal in the project you want to audit and run:

```sh
npx skills@latest add grove/faultline
```

Follow the installer prompts to choose your coding agent and installation scope.
The installer requires [Node.js 22.20.0 or newer](https://www.skills.sh/docs/cli)
and Git; **running an Audit does not require Node.js, Docker, or any project setup**.
This command installs the advice-only `faultline-audit` skill, not an executable
test runner. Installation does not authorize test execution or lift
**NO_GO / UNAVAILABLE**.

## 2. Find important failures

With your project open in your coding agent, ask:

```text
Use faultline-audit to find important bugs my tests might miss.
Don't change files or run tests. Explain the findings and suggest the smallest useful tests.
```

In Codex, you can explicitly invoke `$faultline-audit`. For other agents,
follow their skill invocation instructions. You can also inspect discovery with
`npx skills@latest add grove/faultline --list`. If an agent does not immediately
see the installed skill, start a new agent session.


You can also name a directory, changed files, or a behavior to focus on. You do
not need to identify test commands, supply hashes, or configure a runner.

No configuration or formal risk assessment is needed. Faultline starts from
promises supported by the source, documentation, and callers, then prioritizes
credible failures by consequence, plausibility, weak detection, and whether a
small test would help. Losing confirmed data deserves attention before a minor
formatting gap; low-risk code does not need an invented catastrophe.

Expect up to three findings, ordered by consequence and confidence, with linked
code and test evidence, a plain-English failure scenario, and a concrete test
suggestion. Faultline checks for existing protections and evidence that refutes
each concern. A missing assertion is not automatically an implementation bug.
It distinguishes suspected bugs, missing test protection, and unresolved contract
questions, and always says that tests were not run.

Illustrative finding based on [authored packet A](tests/fixtures/impact-first.json);
this is an expected report, not a model evaluation or an executed test:

> **Confirmed data may disappear after a restart** — suspected implementation bug
> and missing recovery protection.
>
> **What could go wrong:** `Journal.save` calls `acknowledge` before `Disk.sync`.
> A crash in that interval could lose a confirmed record despite the packet's
> documented promise that acknowledged saves survive a restart.
>
> **Why it matters:** users could rely on a successful save and later discover
> that their data is gone.
>
> **Why the existing tests may miss it:** `test_successful_save` checks the
> acknowledgement and the complete recovered value only after `save` finishes.
> It never interrupts the interval before `sync`.
>
> **Smallest useful test:** seed one confirmed record. In the next acknowledgement
> callback, record confirmation, call `Disk.power_loss`, and interrupt `save`
> before it can sync. Reopen a `Journal` on the same `Disk` and assert that both
> complete records are recovered. Keep this in the recovery suite to catch a
> future move of acknowledgement ahead of the durable write.
>
> **Confidence and uncertainty:** the contract, ordering, and modeled storage
> support a suspected bug and protection gap in this packet. Real storage behavior
> and tests outside the packet remain unreviewed. The crash has not been reproduced.
>
> Tests were not run.

If the reviewed scope has no useful finding, Faultline says **No actionable finding
in the reviewed scope.** It gives the scope and reason, including existing
protection where relevant. It does not invent findings to fill a report or claim
the whole repository is correct.

## 3. Turn a finding into a GitHub issue (optional)

Faultline reports findings; it never publishes issues. To draft an actionable issue
from a finding, install [Intentline's issue skill](https://github.com/grove/intentline)
in the same project:

```sh
npx skills@latest add grove/intentline --skill intentline-issue
```

Stay in the **same coding-agent conversation** after reviewing a useful finding.
You do not need to rerun Faultline or copy its report.

**Prepare — review only:**

```text
Use intentline-issue in REVIEW mode to draft one GitHub issue from the
Faultline finding above. Recheck its evidence and expected behavior,
include acceptance criteria and a proposed test, and preserve uncertainty.
Don't publish or change anything.
```

**Publish — only after approving that draft:**

```text
Use intentline-issue in CREATE mode to publish the approved draft as
exactly one issue in OWNER/REPO. I authorize creating this one issue.
Check for duplicates, read back the new issue, and return its URL.
Do not change code or run tests.
```

Replace `OWNER/REPO` with the intended GitHub repository. Publishing requires
your coding agent's existing GitHub issue-write access; installation grants none.
Repeat the review and explicit CREATE request for each additional finding.
Suggested tests remain **PROPOSED — NOT RUN**.

## Verify this finding?

**Verification is not enabled; here is the suggested test.** That is the current
response to an execution request. Audit does not run test discovery, imports,
tests, builds, package scripts, or installation commands, and does not edit files.

An optional **Verify with Docker** experience is planned for repositories you
explicitly trust, with explicit approval before each selected run. It would use an
existing Docker installation, a disposable staged workspace without original or
sensitive host mounts, no network by default, unprivileged execution, bounded
resources, and protected evidence. It would never auto-install Docker.

Docker/Desktop reduces exposure but still has runtime, kernel, daemon, and host
integration risks; it is not a safe place for arbitrary hostile code. See
[Docker's security guidance](https://docs.docker.com/engine/security/).
No Docker execution path ships in this release. Enabling it requires a separate,
explicitly reviewed scope change and approval.

## Manual installation (optional)

If you cannot use the `npx` installer but already have a Faultline checkout,
copy the same standalone skill into another project. Run this from the Faultline
checkout, replacing the target. It refuses to overwrite an existing installation:

```sh
target=/absolute/path/to/your/project
mkdir -p "$target/.agents/skills" &&
  test ! -e "$target/.agents/skills/faultline-audit" &&
  test ! -L "$target/.agents/skills/faultline-audit" &&
  cp -R faultline-audit "$target/.agents/skills/faultline-audit"
```

Installed copies are user-owned; recopy deliberately for updates. The repository
keeps [one canonical skill](faultline-audit/SKILL.md), also used by the `skills` CLI.
No sibling project, hidden runtime, or installation-time code execution is required.

Copy/discovery was checked on 2026-10-18 with Codex CLI 0.163.0 on macOS 27.0.1
arm64. A [live six-case synthetic evaluation](experiments/audit-evaluation/REPORT.md)
on 2026-10-19 used the actual skill through direct-file invocation: three intended
weaknesses found and no false positives on three protected controls, by manual
grading. Read-to-pre-response checkpoints took 9–21 seconds; these exclude final
response generation and startup. No setup was needed by the auditors. These small
authored cases do not establish effectiveness or speed on real repositories.

A [four-repository read-only pilot](experiments/real-repository-pilot/REPORT.md)
completed on 2026-10-19: independent model review accepted 9 of 11 emitted findings
and left two unresolved; one of two predeclared historical gaps was found.
Measured full-response latency was 128–164 seconds, with no runtime setup.
Control-selection limitations and the missed gap limit reliability claims.
The [follow-up diagnosis](experiments/audit-quality-diagnostics/REPORT.md) separates
visibility, contract and timing limits; improved future outcomes remain unmeasured.

A [four-cell packaging comparison](experiments/packaging-2x2/REPORT.md) on
2026-10-20 crossed old/new instructions with absent/present historical specification
text. All four reports missed the targeted interaction; both specification-present
reports retained unsupported installed-mode assertions. That experiment did not
justify further instructions; one run per cell establishes no reliability or
speed gain.

## Maintainer notes

[RO-1: ordinary review versus Faultline](experiments/ordinary-review-comparison/PROTOCOL.md)
is a prepared read-only comparison, **NOT FROZEN / NOT RUN**. Existing evaluations
do not establish incremental value over ordinary review; the current product
decision is **INCONCLUSIVE**. Six candidate scopes are prepared. The user serves
as both human curator and grader; grading is independent of audit workers, not
curation. Budget enforcement and the complete study freeze remain prerequisites.
This phase preserves issue #6's original executable study and dependencies.

A separately authorized [two-case pilot](experiments/ordinary-review-comparison/PILOT-RESULTS.md)
completed four reviews on 2026-10-21 with provisional **NO CLEAR BENEFIT** over
ordinary review; case-level human grading remains pending. The current
**Critical Failure Challenge Loop** is a targeted, unmeasured revision: it makes
promise selection, consequence ranking, and repeatable recovery challenges
explicit while retaining source tracing and active refutation. The
[evaluation hypothesis and next comparison](IMPLEMENTATION.md#3-check-that-audit-helps)
do not claim better detection, accuracy, clarity, speed, or cost. Historical
evaluation instructions and results are preserved unchanged.

[Design](DESIGN.md) · [Implementation plan](IMPLEMENTATION.md) ·
[Security research and unchanged execution gate](ISOLATION.md) ·
[Historical design](DESIGN-HISTORY.md) · [Historical plan](IMPLEMENTATION-HISTORY.md)

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
hashes/syntax and evaluation records. The six [impact-first examples](tests/fixtures/impact-first.json)
specify weak and strong recovery protection, consequence ordering, unclear
contracts, artificial-error tests, and useful negative results. Their checks
validate authored examples and instructions, not observed model reasoning.
These checks do not execute target-project code, the frozen scenario, Docker,
or qualification procedures. Historical research has separate maintainer tests;
it is not part of the Audit workflow.

Apache-2.0; see [LICENSE](LICENSE).
