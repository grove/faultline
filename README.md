# Faultline

**Find weak tests before they miss a real bug.**

Faultline helps your existing coding agent read code and tests, explain realistic
bugs the tests may miss, and suggest the smallest useful test. Audit works without
Docker, dependencies, infrastructure setup, or running your project's code.

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

## 2. Find weak tests

With your project open in your coding agent, ask:

```text
Use faultline-audit to find weak tests in this repository.
Don't change files or run tests. Explain the findings and suggest the smallest useful tests.
```

In Codex, you can explicitly invoke `$faultline-audit`. For other agents,
follow their skill invocation instructions. You can also inspect discovery with
`npx skills@latest add grove/faultline --list`. If an agent does not immediately
see the installed skill, start a new agent session.


You can also name a directory, changed files, or a behavior to focus on. You do
not need to identify test commands, supply hashes, or configure a runner.

Expect a few findings with linked code and test evidence, a plain-English failure
scenario, and a concrete test suggestion. A missing assertion is not automatically
an implementation bug. Faultline distinguishes suspected bugs from missing test
protection, states uncertainty, and always says that tests were not run.

Illustrative finding only; no repository was reviewed or test run for this example:

> **A retry may charge twice** — suspected implementation bug.
>
> **What could go wrong:** a charge succeeds, its acknowledgement is lost, and the
> caller retries the same operation. The retry path appears to record a second
> charge despite the caller's one-charge requirement.
>
> **Why these tests may miss it:** the selected test covers only the first
> successful request.
>
> **Smallest useful test:** lose the acknowledgement after recording a charge,
> retry with the same key, and assert that only one charge was recorded.
>
> **Confidence and uncertainty:** check whether a shared deduplication layer
> prevents the second effect; that would refute the suspected bug.
>
> Tests were not run.

If the reviewed scope has no useful finding, Faultline says so. It does not invent
findings to fill a report or claim the whole repository is correct.

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
reports retained unsupported installed-mode assertions. Keep the guidance
provisionally unchanged; one run per cell establishes no reliability or speed gain.

## Maintainer notes

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
python3 -B -m unittest discover -s tests -p test_spike_design.py -v
python3 -B -m unittest discover -s tests -p test_audit_evaluation.py -v
python3 -B -m unittest discover -s tests -p test_real_repository_evaluation.py -v
python3 -B -m unittest discover -s tests -p test_audit_diagnostics.py -v
```

These inspect packaging, instruction boundaries, links, and frozen fixture
hashes/syntax and evaluation records. They do not execute target-project code,
the frozen scenario, Docker, or qualification procedures. Historical research has
separate maintainer tests; it is not part of the Audit workflow.

Apache-2.0; see [LICENSE](LICENSE).
