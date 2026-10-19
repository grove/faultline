# Faultline

**Find weak tests before they miss a real bug.**

Faultline helps your existing coding agent read code and tests, explain realistic
bugs the tests may miss, and suggest the smallest useful test. Audit works without
Docker, dependencies, infrastructure setup, or running your project's code.

## Find weak tests

Ask your agent:

```text
Read /absolute/path/to/faultline/faultline-audit/SKILL.md and find weak tests
in this repository.
```

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

## Optional skill discovery

The direct-file prompt above needs no installation. To make the skill discoverable
in another project, run this from your Faultline checkout, replacing the target.
It refuses to overwrite an existing installation:

```sh
target=/absolute/path/to/your/project
mkdir -p "$target/.agents/skills" &&
  test ! -e "$target/.agents/skills/faultline-audit" &&
  test ! -L "$target/.agents/skills/faultline-audit" &&
  cp -R faultline-audit "$target/.agents/skills/faultline-audit"
```

Invoke `$faultline-audit` with “Find weak tests” and optional paths. Installed
copies are user-owned; recopy deliberately for updates. The repository keeps
[one canonical skill](faultline-audit/SKILL.md). No sibling project is required.

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
