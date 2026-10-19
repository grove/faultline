# Faultline product design

**Direction changed on 2026-10-19:** easy to use, easy to understand, easy to
operate, and useful for discovering tests that miss real bugs, in that order.
The default product is read-only Audit. Optional Docker verification is proposed
and disabled. The existing execution decision remains **NO_GO / UNAVAILABLE**.

## One simple workflow

**Find weak tests → understandable findings → Verify this finding? → clear result.**

Use the existing portable `faultline-audit` skill and the developer's existing
coding agent. No new application, model controller, service, CLI, or framework.
Audit must work immediately without Docker or runtime setup. It is optional,
never a mandatory PR gate or a dependency on another project.

## Default: Audit

Input is a repository or selected paths, optionally a behavior question. Infer
relevant callers and tests from source. Start with a consequential behavior and
state the scope; do not require a formal guarantee or candidate manifest from the
developer. Missing requirements become explicit uncertainty or a focused question,
not an invented contract.

Read files as data; do not execute project imports, discovery, tests, builds,
plugins, package scripts, or installs. Do not probe Docker or start infrastructure.
Do not edit code, tests, or reports without separate write authority.

Return up to three findings: what could go wrong, why these tests may miss it,
the smallest useful test, and confidence and uncertainty. Link the code/tests
actually read and the source of the expected behavior. Distinguish suspected
implementation bugs from missing test protection; check valid alternatives and
possible refutation. Missing assertions do not establish defects or passing tests.
Say **Tests were not run.** A useful negative result is **No actionable finding in
the reviewed scope**, with the scope and reason. Avoid scores, generic coverage
advice, mandatory mutation plans, and claims of overall correctness.

Keep available snapshot identity (including relevant dirty content), source/test
locations, and evidence distinctions in internal working notes. Unknown identity
does not block advice. Keep hashes, VM details, launchd, lifecycle operations,
qualification receipts, and accounting ledgers out of ordinary reports; expose
technical detail on request. No new report store or receipt schema is needed for
Audit, and no private material is exported implicitly.

## Optional: Verify with Docker — proposed, disabled

Today, “Verify this finding?” receives **Verification is not enabled; here is the
suggested test.** Do not solicit per-run approval as if a verifier already exists.
An execution request does not activate a host-shell fallback.

A separate, explicitly reviewed scope change and approval must precede enabling
any Docker execution. Current host/tool qualification and caller-authorization
requirements remain in force until that separately approved change explicitly
defines the narrower trusted-repository boundary. Trust is not qualification.

The smallest later implementation supports one Python test workflow with existing
test tools and one Docker adapter, with these requirements:

- **Explicit trust and opt-in:** show the finding, proposed test, exact command,
  limits, and residual risks before approval. Bind approval to the snapshot and
  effects; changed inputs or commands require renewed approval.
- **Existing prerequisites:** use existing, running local Docker and a reviewed
  local image with dependencies already present. Never auto-install, start the
  daemon, pull/build images, execute repository Dockerfiles/Compose, or enable
  network to repair prerequisites. Report unavailable instead.
- **Disposable input:** stage selected files, including relevant local edits,
  without hooks or links escaping scope. Exclude credentials, metadata, sensitive
  files, and inherited host environment/sockets. Do not hard-link originals or
  mount originals or sensitive host paths.
- **Restricted execution:** no network by default (no override initially), ports,
  host namespaces, Docker socket, privileged mode, or elevated capabilities.
  Use a non-root user, read-only root, disposable writable storage, and finite
  CPU, memory, process, wall-time, output, and writable-storage limits. Stop if
  selected limits cannot be enforced.
- **Protected evidence:** a host-controlled collector outside container writes
  records the snapshot/commands, bounded output, statuses, and limits. Container
  logs and generated files are untrusted inputs, not authoritative receipts.
  Preserve evidence distinctions and check original/source identity.
- **One test, unchanged implementation:** run selected existing tests on the staged
  baseline, then the proposed regression test in fresh state on the same unchanged
  implementation. No mutations or automatic production fix. Stop attribution on
  baseline failure/flakiness, drift, timeout, setup error, or unclear expectation.
- **Bounded operation:** host-controlled timeout and cleanup of only created
  identities. Incomplete cleanup is an operational failure, never a successful run
  or permission to repeat silently.

| User-facing result | Meaning |
| --- | --- |
| Bug reproduced | Selected baseline tests pass; the new test demonstrates an attributable violation of the source-grounded expectation in unchanged code. |
| Not reproduced by this test | Baseline and proposed test pass; this condition did not expose a bug. A protection gap can still merit the test. |
| Could not determine | Baseline failure, flaky behavior, ambiguous assertion, timeout, drift, or incomplete observation prevents attribution. |
| Verification unavailable | Permission, approved prerequisites, enforcement, or protected evidence is missing; no verification verdict. |

Suggested trust prompt: “Only verify repositories you trust. Docker reduces
exposure but still has runtime, kernel, daemon, and Desktop integration risks.
It is not qualified for arbitrary hostile code.” Docker documents
[daemon and kernel risks](https://docs.docker.com/engine/security/) and
[Desktop host permissions](https://docs.docker.com/desktop/setup/install/mac-permission-requirements/).
The warning never substitutes for required controls.

## Research and scope boundaries

[ISOLATION.md](ISOLATION.md), all qualification source/receipts and terminal NO-GO
evidence, and the [frozen NOT RUN spike](experiments/lost-acknowledgement.md) remain
intact. They are security research, not ordinary-user setup steps or permission
to execute. Unavailable launches do not establish denied effects.

Custom VM runners, QEMU, Firecracker, and additional Apple Container qualification
are deferred. No mutation engine, backend registry, dashboard, mandatory CI gate,
language expansion, automatic fixes, or publication workflow is needed.

The [historical design](DESIGN-HISTORY.md) preserves experiment semantics and
research; the [historical plan](IMPLEMENTATION-HISTORY.md) preserves the NARROW
decision and earlier issue map. Their build order is superseded, not evidence that
safety controls passed. No tracker states are changed. Faultline does not alter
sibling projects or their frozen candidates/receipts.

## Value before infrastructure

Assess Audit on a few real historical bug snapshots and clean controls as source
data, without executing them. Look for relevant small tests, false alarms,
understandable explanations, and time to a useful finding. Known-answer
walkthroughs check usability, not independent discovery. Record unknown timings
honestly. If ordinary direct review is equally useful, simplify rather than
adding infrastructure.
