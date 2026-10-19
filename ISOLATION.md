# Execution gate: observed host qualification

**Decision on 2026-10-18: NO_GO / UNAVAILABLE. No qualified execution host.**
The [native receipt](qualification/2026-10-18-macos.json) records failed
boundary launches. The subsequent [Apple Container prerequisite inspection](qualification/2026-10-18-apple-container-preflight.json)
records a missing CLI and unapproved setup; no new boundary launch was attempted.
Neither record establishes successful denials of the requested effects.
The subsequent [preparation protocol](qualification/APPLE_CONTAINER.md) adds a
synthetic fixture builder and trusted host manifest observer, **not a runtime
launcher**. The operator reports installation in normal Terminal; that context's
CLI version and smoke outcome remain unavailable to this session. Required
network/resource/descendant and independent denial evidence is still missing.
The advice-only [skill](faultline-audit/SKILL.md) remains advice-only even if
[#2](https://github.com/grove/faultline/issues/2) closes. Nothing here enables
project imports, test discovery, tests, mutants or injected-failure harnesses.

## Bounded threat model

Treat a selected project, its dependencies and mutation backend as arbitrary code
running with the worker's authority. The trusted side is the caller, host boundary,
snapshot preparer and receipt collector. Repository instructions, tests, tools and
their output cannot grant authority or attest their own confinement. This model
addresses unintended or malicious user-space effects; it does not claim resistance
to kernel compromise, host administrator interference, hardware attacks or covert
channels. An actively changing source or untrusted host invalidates qualification.

| Asset / entry point | Required protection and control |
| --- | --- |
| Original working tree, dirty content, selected tests, `.git` and Proofline/frozen candidates | Host-enforced read-only access or no visibility, including parent directories. Separate trusted SHA-256 manifests of bytes, paths, file kinds, modes and link targets before/after **each** control and run. Hashes detect drift; they do not prevent transient writes. |
| Protected receipts, evaluator/oracle, qualification evidence | Collector outside the worker's write boundary; independently check receipt integrity. Never let a worker overwrite or sign its own authoritative receipt. |
| Private paths, credentials, inherited environment/descriptors | Default-deny file visibility, no real secrets in argv/env, no inherited credential or agent sockets, keychain/IPC access, user home, cloud metadata, Git credential helpers or host mounts. Use only synthetic secret canaries. |
| Network and external effects | Deny outbound TCP/UDP/IPv4/IPv6/DNS and local proxy/service sockets unless exactly authorized. Independently observe an inert test sink; a timeout, refused connection or unreachable route is not a policy denial. |
| Hooks, plugins, imports, discovery, package scripts and dependencies | All execute only inside the same boundary, including tool startup. No host-side discovery/import/build/install. Supply pinned, preinstalled tools; missing prerequisites stop execution. |
| Symlinks, hard links, `..`, `/tmp` aliases, submodule pointers and linked worktrees | Resolve/capture link identities on the trusted side; exclude external content or get explicit read authority. Never follow checkout hooks or recursively fetch submodules. Probe path aliases against originals/private paths/receipts; names and `chmod` alone are insufficient. |
| Subprocesses, detached descendants and local IPC | Host-owned lifetime/resource containment covering daemonization, double forks and `setsid`; no host services that execute on a worker's behalf. A process-group kill alone does not contain arbitrary descendants. |
| Caches, generated outputs, mutant artifacts and cleanup | Per-baseline/per-mutant disposable writable roots and HOME/TMPDIR/cache directories. No host cache reuse or shared writable tests. Cleanup only host-created identities; never follow worker links or recursively delete a supplied project path. |

Approved candidate/test inputs are immutable to audit commands. Stage copies from
the trusted side without running project code. A baseline and each mutant get
independent copies and output roots; mutate production bytes only. Keep retained
evidence elsewhere. Verify both immutable originals and unchanged test copies
after every step; drift stops the run and invalidates attribution. Do not repair
drift by silently restoring bytes and continuing.

## Current preparation: Apple Container 1.5.0 — UNAVAILABLE pending controls

The authorized setup-v2 attempt started four services in `user/501`, then failed
Faultline's raw path comparisons. API roots had no trailing slash; plugin roots
did. The original receipt is preserved byte for byte, and independent read-only
launchd/plist inspection identifies all four services in the dedicated setup-v2
root. See the [separate recovery proposal](qualification/APPLE_CONTAINER_RECOVERY_02.md).
Recovery-01 then stopped on unscoped process parsing, with no removal attempted.
**Fresh recovery-02 approval is the next action; do not retry startup or provision images.**
No cleanup or VM execution has run. Setup-v1, setup-v2 and Stage 1a authority are
consumed. Earlier preparation/inventory receipts and frozen source identities
remain unchanged; execution-time inventory code identity remains operator-corroborated.

The latest [staged authorization proposal](qualification/APPLE_CONTAINER_NEXT.md)
adds a frozen positive-v2 fixture with host acknowledgement before tmpfs teardown,
fresh preparation and a separately authorized service-inventory command. It
proposes a 2-vCPU / 512-MiB VM ceiling with a 1-CPU / 256-MiB workload (predicted
VM allocation 2 vCPUs / 384 MiB). The consumed setup-v2 approval allowed service startup and pinned-init retrieval;
no VM budget change or guest execution has been approved or performed. Positive execution still needs verified
artifacts and independent host-owned VM deadline/termination; a successful smoke
test would not qualify the sandbox. Prior records below remain historical.

Review the [implementation and exact Terminal procedure](qualification/APPLE_CONTAINER.md)
and [operator-provided Terminal inspection](qualification/2026-10-18-apple-container-terminal.json).
It reports Container **1.5.0 / d265d66** at `/usr/local/bin/container`, SHA-256
`8cc619377e8978a0ce9f22a3e864dcd4445f2bc38fb64c5197bb69a1bab42463`,
on macOS **27.0.1 / 26A434**, arm64. All version/help requests succeeded,
untruncated. This is a reserialized pasted report, not independent host or vendor
attestation; original-file hash and checkout commit were not supplied. All eight
source hashes matched the pre-edit workspace. Possible CLI-internal service contact,
helpers and side effects were not independently observed or excluded.

The [version-matched review](qualification/2026-10-18-apple-container-review.json)
pins Container source `d265d669ecae041bf338cb3b39c4118316d138f0`, its locked
Containerization 0.47.0 dependency, and reviewed document/source content hashes.
It retains help-matched candidate argv, including source-supported `--network none`
(zero attachments); omitted networking selects the default. That is source review,
not evidence of installed enforcement. Image/init/kernel provenance, effective
environment, aggregate resource/output/deadline limits, calibrated independent
denial/VM/process observers and cleanup remain unverified. Runtime argv is incomplete
and **NOT AUTHORIZED**; even positive startup is blocked.

The operator has now prepared `/private/tmp/faultline-apple-review-01`. Its
[unaltered receipt](qualification/2026-10-18-apple-container-prepared.json) matches
the separately supplied SHA-256
`3349e3c1e401afa9c32de55ecd385cd65afc46b01fcfbb7660d1c0f763f4426d`;
all eight source hashes and five protected-tree manifests match. The hashed protocol
and fixture remain unchanged. Follow the latest
[positive-smoke supplement](qualification/APPLE_CONTAINER_POSITIVE.md), rather than
repeating the historical preparation instructions. It pins a candidate worker
manifest from registry metadata only; no image layers were downloaded.

The [positive review evidence](qualification/2026-10-18-apple-container-positive-review.json)
records strict installed-CLI signature verification failure in this session and
a denied capacity query. The later
[operator-provided normal-Terminal results](qualification/2026-10-18-apple-container-terminal-prerequisites.json)
report valid Apple-signed code, a matching embedded CDHash, arm64, 10 logical CPUs,
32 GiB RAM and hardware virtualization support. The earlier restricted-session
results remain context-specific observations, not evidence of tampering. Matching
source predicts that `--cpus 1 --memory 256M` sizes a 2-vCPU / 384-MiB VM,
including overhead, exceeding the earlier proposed whole-VM ceiling. No ceiling
increase is approved. Local artifact identities, aggregate enforcement, calibrated
observers, independent tmpfs-marker retention and cleanup remain unavailable.
The approved normal-Terminal prerequisite checks are completed as reported; no
repeat collection or reapproval is needed. No positive launch is ready for approval
while artifact, enforcement, independent-observation and cleanup gaps remain.
No canary, service, image/init/kernel retrieval or project code was executed.
Preparation/observer unit checks are not qualification; all 33 runtime controls
remain **NOT_RUN**.
**Keep #2 open; execution remains NO_GO / UNAVAILABLE.** The earlier records below
describe their original host context and are not reclassified by the operator's
subsequent installation report.

## Next candidate: Apple Container — UNAVAILABLE before setup

Historical prerequisite inspection, retained for the original host context:

The read-only follow-up for [#2](https://github.com/grove/faultline/issues/2)
selects **Apple Container only** for the next qualification. It does not implement
a runner or select another backend when prerequisites fail. **Keep #2 open:**
the required positive child and independently observed protections remain missing.

**Recorded host:** `faultline-mac-codex-workspace-write-2026-10-18`, a local
session label, not a hardware attestation. Actual observations are macOS 27.0.1
build 26A434, Darwin 27.0.0, arm64, with the existing restricted-network and
workspace-write Codex configuration. The `sysctl` prerequisite query returned
`Operation not permitted`; virtualization availability and resource capacity
remain **UNKNOWN**. No query was retried with weaker host restrictions.

| Option inspected | Evidence and selection |
| --- | --- |
| **Apple Container — selected** | No `container` on the recorded search path or at `/usr/local/bin/container`, `/opt/homebrew/bin/container`, `/usr/bin/container`. CLI/version/image digest and version-matched help are **UNAVAILABLE**. Installation is not authorized. |
| Installed Docker | CLI 29.9.1, build `dfc520dcc2`, and `/Applications/Docker.app` present. Retained `--version` and `--help` are client-only evidence. No daemon, image, socket, context or confinement inspection; not selected. |
| Separately provisioned disposable VM — deferred fallback | No provisioned VM identified by this bounded inspection; no VM is started. Would require a different, explicitly approved host/configuration with only fixture inputs and no sensitive shared folders. |
| Native `sandbox-exec` — historical evidence only | Prior twelve launches failed before child startup. No retry; deprecated launcher and missing containment/resource evidence do not qualify it. |

The inventory also checks named alternative CLIs and common app locations; a
missing result means **not found in those locations**, not proof that no copy or
VM exists anywhere on the host. Docker's own [security documentation](https://docs.docker.com/engine/security/)
describes the daemon's authority; client presence alone supplies no boundary
evidence. No Docker control socket is offered to a worker.
The retained help also reports `debug`/`init` plugin metadata failures despite
exit zero; plugin discovery is not a runtime health check. **The `docker --help`
command may invoke Docker CLI plugin binaries to obtain their metadata.** The
failures are consistent with attempted plugin discovery but do not establish
which helper processes actually started, what they did, or whether they caused
side effects. No independent process/side-effect telemetry was collected. Thus
**zero boundary launches** and **zero synthetic challenge children** mean only
that no VM/sandbox qualification experiment was launched; they do **not**
establish zero subprocesses or a fully side-effect-free host inspection.
"Read-only preflight" describes the intended scope (no requested changes), not
a verified OS-level read-only execution guarantee. The retained JSON contains
the original observations; this clarification does not reclassify them.

Apple's [project requirements](https://github.com/apple/container#requirements)
describe Apple silicon and macOS 26 support, but do not establish compatibility
with this exact host. Its [command reference](https://github.com/apple/container/blob/main/docs/command-reference.md)
was reviewed on 2026-10-18 as **current-branch research**, not version-matched
installed behavior. It documents root `--read-only`, separate read-only mounts,
CPU/memory settings and networking. Root read-only mode does not by itself
protect other mounts. `--internal` is host-only networking; `--no-dns` only omits
DNS configuration. Neither establishes full network denial. No proposed launch
argv is supplied: exact flags must first be verified against a pinned installed
CLI and matching release documentation. CLI, image and init/kernel provenance
remain unpinned because nothing was installed or retrieved.

### Permissions and retained evidence

The current request authorizes this inspection, repository edits and PR creation.
It does **not** authorize installation, image/kernel retrieval, service startup,
host changes, synthetic VM launches or network probes. None was attempted.
Read-only documentation access and GitHub publication are distinct from runtime
network authority. No target-project or #10 code ran; the native canary coordinator
was not rerun. No executable skill behavior is enabled.

The [preflight JSON](qualification/2026-10-18-apple-container-preflight.json)
retains UTC time, source commit and SHA-256 identities **before these documentation
edits**, bounded lookup paths/results, exact inspection argv/cwd/environment,
exit/stdout/stderr with documented path redaction, elapsed command/inspection time,
permission gaps and every
unrun control. It was collected by trusted standard-library host inspection,
outside any worker; no worker exists in this attempt. The cwd is redacted as
`<faultline-checkout>` and the Docker help's home prefix as `<host-home>` (with
the original stdout SHA-256 retained); no machine serial, credential configuration, environment
dump or authentication material was collected. The elapsed field covers the
recorded local inspection only; documentation research and PR work are separate
and unmetered. No runtime objects, fixtures or writable host mounts were created,
so there is no VM/fixture cleanup to claim and no descendant cleanup evidence.
The earlier native receipt is retained unchanged. Zero boundary-child counts
refer to this preflight, not the separate maintainer checks documented in README.

### Required next controls — all NOT RUN / UNQUALIFIED

After separate setup approval, review and approve **one** synthetic protocol with
exact CLI/image/fixture hashes, argv, cwd, allowlisted environment, scratch and
host-owned receipt destinations, observer identities, inert endpoints, finite
budgets and identity-scoped cleanup. This is a review checklist, not launch
authority or an executable command template:

| Control | Required independent evidence before a qualified decision |
| --- | --- |
| Positive smoke test first | Approved Python child actually starts, reads immutable input and writes only disposable scratch; host observes startup, expected output and unchanged protected manifest. Stop if this fails. |
| Protected files and private paths | Actually attempt source/test/receipt writes and renames, synthetic credential/private reads and unrelated-directory access. Capture explicit policy denials and trusted before/after manifests of bytes, kinds, modes and links after **each** attempt. Unchanged hashes alone do not prove denial. |
| Alias and mount protection | Probe symlinks, hard links, `..`, source identity and read-only inputs with fresh state for each attempt. No retained writable host bind mounts, home/keychain/SSH/cloud/daemon sockets, forwarded agents or inherited sensitive descriptors. |
| Outbound and host-facing network | Approved inert sinks and an independent host observer for TCP/UDP, relevant IPv4/IPv6, DNS, gateway/host-only routes, local service/proxy/socket paths. A timeout, refusal, absent DNS or guest message is insufficient. No real production endpoints. |
| Host-owned lifetime and limits | Bound time, memory, processes, CPU and output; exercise children and detached descendants. Independently observe VM termination and no lingering descendants after normal completion, timeout and interrupted cleanup. A process-group kill is insufficient. |
| State, receipts and cleanup | Fresh immutable candidate and scratch per attempt; verify originals/protected receipt identities after every control. Keep authoritative evidence outside worker writes; clean only created identities without following worker links. Stop on drift or incomplete observation. |

Unavailable or unsafe controls remain **UNAVAILABLE / UNQUALIFIED**, never PASS.
Even successful synthetic qualification would apply only to its exact host,
versions and configuration, require independent review, and would not enable
`faultline-audit`, mutations, project tests or the #10 experiment.

**Decision: NO_GO / UNAVAILABLE.** Smallest next action: separately approve
identity-scoped recovery of the existing setup-v2 services. Further startup,
provisioning and the reviewed synthetic protocol require later authorization. This PR
does not request blanket installation or experiment authority. Do not escape the
current Codex restrictions or install a substitute runtime to complete a receipt.

## Historical native mechanism, and its limits

The considered mechanism is macOS's **native Seatbelt launcher,
`/usr/bin/sandbox-exec`**, with a default-deny host policy. It delegates enforcement
to the OS; Faultline supplies no sandbox implementation or project runner.
The installed Apple `sandbox-exec(1)` manual calls this utility **deprecated** and
directs application developers to [App Sandbox](https://developer.apple.com/documentation/security/app-sandbox).
That application capability is not evidence that a CLI launch is confined.

**Host scope examined:** macOS 27.0.1 (26A434), Darwin 27.0.0, arm64, inside this
Codex session's workspace-write/filesystem and restricted-network boundary.
**Supported qualified hosts: none.** Linux, Windows, other macOS versions, a plain
Terminal session, containers and remote workers have not been qualified. The
parent agent boundary allows workspace writes and reads beyond the selected
candidate; it cannot establish immutable originals or private-file protection.

The native launcher refused all twelve synthetic launches with exit 71 and
`sandbox_apply: Operation not permitted`. No child-start marker was emitted.
This demonstrates an unavailable nested launch, **not** enforced denial of writes,
reads or network access. Do not retry outside the agent sandbox to turn this into
a success. A differently provisioned host requires a separately authorized,
fresh qualification with its own receipts.

Seatbelt alone also supplies no demonstrated aggregate CPU/memory/process/output
quota or trusted descendant cleanup in this experiment. Its policy must be
reviewed on the specific host; these probe rules are deliberately **not an
approved policy for arbitrary project code**. Host changes, toolchain changes,
policy changes, mounts, inherited handles or network allowances invalidate any
prior qualification. No portable safety claim follows from these observations.

## Reproduce the bounded synthetic controls

This is maintainer qualification work, outside the advice-only skill. Read the
[probe](qualification/macos_canaries.py) first. It accepts no project path or test
command and uses only the standard library and installed native tools. Prerequisites
are macOS, Python 3.10+ for the coordinator, `/usr/bin/python3` for synthetic
children and `/usr/bin/sandbox-exec`; install nothing automatically.

With caller authority for synthetic temporary files, these exact synthetic argv
and a **new** local receipt destination, from the Faultline checkout:

```sh
python3 -B qualification/macos_canaries.py > /tmp/faultline-isolation-receipt.json
```

Choose a fresh destination to avoid overwriting a retained receipt. This is not an
invocation path from the skill, and the probe always returns `UNAVAILABLE`; it
does not issue a reusable execution grant. The coordinator creates a fresh
disposable root with `original`, `protected`, `private`, `baseline` and `mutant`
siblings. Only baseline/mutant are writable in the proposed native policy; the
private synthetic token is unreadable. No private target repository is accessed.
The JSON records exact profile/argv/environment, probe identity, host, each native
exit/stdout/stderr, timing and original candidate/test/receipt/private hashes.
Each command is the recorded `argv_prefix` plus that control's `argv_suffix`;
its working directory is `<synthetic_root>/mutant`. Standard input is closed to
the child, and only the recorded environment is passed.
Its temporary artifacts are removed separately from the retained JSON.

| Control | Required observation | This host |
| --- | --- | --- |
| Read original / write mutant output (positive controls) | Child started and intended access succeeded | UNAVAILABLE; launcher failed |
| Write original source, selected tests and protected receipt | Child started; explicit access-policy denial; each original unchanged | UNAVAILABLE; launcher failed |
| Read synthetic private token | Child started; explicit access-policy denial | UNAVAILABLE; launcher failed |
| Write/read through symlinks, hard-linked receipt, `..` | Explicit denial, originals unchanged after each | UNAVAILABLE; launcher failed |
| Outbound TCP to documentation-only `192.0.2.1:9` | Explicit policy denial; independent network observer sees no effect | UNAVAILABLE; launcher failed; no observer established |
| Ten-second sleeper under two-second deadline | Timeout, host-owned cleanup and independently observed absence of descendants | UNAVAILABLE; sleeper never started |

Twelve boundary-launch attempts, zero synthetic child starts, zero project test
or mutant executions. All four protected synthetic file hashes matched after
every attempt; the disposable root was removed. This is unchanged-source evidence
for failed launches only. No protected-read or network denial was established.

The coordinator has a 30-second scheduling budget, two seconds per launch and a
one-second cleanup wait; it kills/reaps its created process group. Maintainer
checks demonstrate killing a cooperative synthetic sleeper, **not** arbitrary
descendant confinement. Captured output is retained up to 4096 bytes per stream;
the fixed synthetic probes have bounded output. Pipe capture is not a memory/output
limit for untrusted code. Detached descendants, fork/output/resource exhaustion,
DNS/UDP/IPv6/local socket effects, keychain/credential IPC, submodule traversal,
cache aliases, file replacement/rename/mode changes and transient write/restore
attacks remain **UNESTABLISHED**. A future host must supply limits and corresponding
negative controls before any project launch. Do not treat passing this small
probe set as sufficient qualification.

## Qualification and effect authorization are separate

Before a future execution release, an independent host operator must record a
reviewable qualification for the exact boundary and commands. Positive controls
must work; protected operations must actually be attempted and denied. Collect
host telemetry rather than trusting worker claims. Verify manifests and absence
of descendants after each control, including timeout and interrupted cleanup.
Expand the controls above for every unestablished required protection. Any allowed
forbidden effect, ambiguous result, missing prerequisite or telemetry gap fails
qualification. Requalify on drift; never weaken a policy merely to make tests run.

| Effect | Necessary caller/host authority |
| --- | --- |
| Qualification canaries | Exact synthetic launches, disposable file read/write/cleanup and inert network probes on the specified host; no real credentials/services. |
| External tool installation | Separate explicit tool/version/source, destination, install/build scripts, network and cost authority. An executable in a plan is not install permission. |
| Read source or fixtures | Exact candidate, relevant dirty content, selected files and any submodule/link targets; no implied home/private repository access. |
| Run tests/mutants/harnesses | Future execution-enabled release **and** current qualification, exact approved executable argv/cwd, versions, snapshot, effects and finite budgets. Opting into advice is insufficient. |
| Write reports/artifacts | Authorized destination, retention/privacy limits and cleanup scope. Conversation advice alone needs no disk write. |
| Network, paid models, publication, PR, push, merge | Separate authority for the particular effect and data destination. Qualification, PR creation and merge readiness never authorize merging. |

**Fail closed:** no verified isolation means `NO_GO / UNAVAILABLE` for execution.
Provide an advice-only plan with candidate/source identities (or UNKNOWN), the
selected question/test path, proposed argv marked NOT_RUN, smallest direct
assertion, missing protections and required authority. Do not fall back to an
unprotected shell with a warning. Permission failures and missing tools are
`UNAVAILABLE`; timeouts, broken baselines, interrupted cleanup or ambiguous
attribution are `INCONCLUSIVE`. None is a test-strength success, KILLED mutant,
SURVIVED mutant, observed implementation violation or correctness certificate.
