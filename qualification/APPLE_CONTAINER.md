# Apple Container qualification preparation — NOT RUN

Related to [#2](https://github.com/grove/faultline/issues/2); keep it open.
**Decision: UNAVAILABLE; execution NO_GO.** This is a preparation harness and
review procedure, not a qualified runner. It has no container-launch command,
GO override, installation, image retrieval, service startup or automatic cleanup.
Only the fixed filesystem fixture is implemented. Network, resource and lifetime
controls are specified below and remain unavailable, not passing placeholders.

The operator supplied normal-Terminal inspection JSON at
`2026-10-18T20:22:22.245494+00:00`, retained as
[client evidence](2026-10-18-apple-container-terminal.json). It reports Container
**1.5.0**, release commit **d265d66**, at `/usr/local/bin/container`, SHA-256
`8cc619377e8978a0ce9f22a3e864dcd4445f2bc38fb64c5197bb69a1bab42463`.
The host reports macOS **27.0.1 / 26A434**, Darwin **27.0.0**, **arm64**,
Python **3.15.0**. All seven host/version/help observations exited zero, with
empty stderr and no truncation. This confirms the operator-reported client
identity and supported help syntax; vendor signature, binary-to-release match,
hardware identity, service state and runtime behavior are not attested.

The JSON was transcribed from the operator's pasted report and reserialized,
without path redaction. The original local file hash and checkout commit were
not supplied; no original-byte hash is claimed. All eight reported source hashes
matched the workspace before these edits, including this protocol's then-current
`100561772b591cf0c665103730bf6a8b88f40de829bdfaffb5a0b1a3c04e9774`.
Later protocol edits do not invalidate that historical identity. The earlier
missing-CLI receipts describe the restricted Codex context and remain unchanged.
The reported past smoke test still has no retained command or outcome. All 33
qualification controls remain **NOT_RUN**; no boundary launch is recorded.

## First Terminal evidence: client inspection only

In the normal macOS Terminal, confirm the checkout belongs to draft PR #17:

```sh
cd /Users/grove/projects/faultline
git branch --show-current
git rev-parse HEAD
```

The branch must be `issue-2/apple-container-qualification`; compare the commit
with PR #17's current head. Stop on a mismatch rather than checking out another
branch over local changes. Retain the commit alongside the inspection JSON.
Then run this exact command from that directory. It requests host/CLI identity
and client help, with no intentional file writes, service startup, downloads or
runtime operations. **Possible CLI-internal service contact, helper processes
and side effects are not independently observed or excluded.**

```sh
python3 -I -B qualification/apple_container.py inspect
```

It records macOS/build, architecture, Python, CLI path/SHA-256, exact argv,
allowlisted environment, return codes and help. Each client command has a
five-second timeout. The subprocess stdin is closed and unrelated descriptors
are closed by Python. CLI-internal helper processes and side effects are not
independently observed by this inspection; help is not a runtime safety check.
No full environment, credentials, shell configuration or
project imports are read. Help is capped at 64 KiB per stream **when retained**;
capture assumes trusted installed client help has finite output, not an output
quota for arbitrary code. Retain the complete JSON locally; inspect it before
sharing paths. An absent CLI, timeout, truncated help or failed help command
blocks the next stage. Do not install, start or pull to fix an inspection failure.
Paste the complete JSON or provide the saved JSON file after reviewing paths and
identifiers. Keep the raw original locally; publish only a reviewed copy with
redactions identified and the raw file's SHA-256 retained. Do not replace any
historical receipt or relabel this inspection as execution-safety qualification.

For subsequent inspections retain the same provenance. The supplied inspection
has now been compared with the observed release's sources, as recorded below.

For each proposed flag, record the exact installed-help excerpt, matching tagged
documentation URL/commit/hash, intended enforcement and independent observation.
Compare root and bind-mount read-only settings, entrypoint/environment, network
attachments, resource limits and identity-scoped stop/delete behavior. Report an
absent or conflicting flag as a blocker. In particular, neither `--internal`
(host-only networking) nor `--no-dns` establishes denial of all external and
host-facing networking. Do not infer that an unconfigured network means no network.

## Version-matched review and blocked command specification

Apple's [1.5.0 release](https://github.com/apple/container/releases/tag/1.5.0)
resolves to `d265d669ecae041bf338cb3b39c4118316d138f0`, matching the CLI's
reported short commit. Its
[command reference](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/docs/command-reference.md)
matches the captured run/inspect/stop/delete/image-inspect syntax used below.
The tagged and commit-pinned reference and `Package.resolved` bytes were compared
and matched. The lock pins Containerization **0.47.0**, revision
`bc994b88df46207fad7775b0eabc51947e315881`; this is a source dependency identity,
not an observation of installed helper binaries. See the
[review record](2026-10-18-apple-container-review.json) for immutable URLs,
SHA-256/content lengths of twelve reviewed documents/source files, release-body
hash, exact candidate argument arrays and every unresolved field. Documentation
retrieval downloaded text only, with no image, init or kernel artifact retrieval.

| Installed-help evidence | Matching source and review result | Required independent evidence |
| --- | --- | --- |
| `--read-only`: root filesystem read-only; `--mount`: `type=<>,source=<>,target=<>,readonly` | `Flags.swift`, `Parser.mount`, `Utility.containerConfigFromFlags`: separate read-only root and two `virtiofs` mounts, only synthetic `original` and `inputs` | Actual mount/namespace/inode configuration, calibrated denial observations and protected manifests; unavailable |
| `--network <network>`; `--no-dns` | `NetworkClient.noNetworkName` is `none`; Utility maps that sole network argument to zero attachments. Omitted network selects the default. Generic help/reference do not describe this reserved value; pinned source supplies that detail | Verify actual zero network devices/routes and denied IPv4/IPv6 TCP/UDP/DNS/host/Unix-socket effects with calibrated observers; unavailable |
| `--cpus <cpus>`; `--memory <memory>` | One CPU and `256M` are proposed values; locked `LinuxContainer.swift` configures CPU/memory cgroup limits, separately from VM sizing | Inspect actual VM and aggregate limits; neither allocation text nor source proves installed enforcement |
| `--tmpfs <tmpfs>` | Parser accepts `destination:comma-separated-options`; proposed `/scratch:size=16m,mode=0700,uid=65534,gid=65534` is a guest mount, with no writable host bind | Verify effective ownership/options and cap all writable guest storage, including default runtime mounts; unavailable |
| `--uid`, `--gid`, `--cap-drop` | Proposed UID/GID `65534`, capabilities `ALL` dropped, no privileged additions | Verify effective identity/capabilities and readable synthetic inputs; image not selected |
| `--ulimit <limit>` | Tagged `docs/ulimits.md` describes init-process Linux rlimits. `nproc`, `cpu`, `fsize` do not establish the required aggregate PID, wall-time or total-storage/output ceilings | Aggregate 16 PIDs, 64 KiB output, total storage and host-owned deadlines remain unavailable; no invented `--pids-limit`, `--timeout`, `--pull=never` or output flag |
| `--entrypoint <cmd>`, `--workdir <dir>`, `--env <env>` | Explicit interpreter and `/scratch` required. Parser merges image environment with explicit values; bare env names inherit host values | Pinned image/interpreter and complete effective environment allowlist missing; explicit `--env` alone does not clear image variables |
| `inspect <container-ids>`, `stop --time <time> <container-ids>`, `delete <container-ids>` | Candidate ID `faultline-apple-review-01-positive`; one-second stop grace; delete only after independently observed stop | First establish exact owned VM/helper identities and absence of a pre-existing name; normal/timeout/interruption recovery unverified. No `--all`, `--force` or auto-remove |

The review record deliberately stores an **incomplete argv specification**, not
an executable launcher: image/init/kernel digests, interpreter path, host environment,
independent observer commands and enforced aggregate limits are null/unavailable.
Its fixed positive tail is `-I -S -B /inputs/guest.py positive`; it must never be
run on the host. Each adverse filesystem control would need a fresh bundle and
new owned identity; the network/resource/lifetime controls remain unimplemented.
The candidate inspect/stop/delete arrays are also **NOT AUTHORIZED**, including
service contact. They are not proof of full descendant termination or recovery.

`ContainerRun.swift` calls the artifact-resolution path in `Utility.swift`, which
can fetch image/init content. A digest alone would not make startup offline;
there is no captured no-pull option. Existing image, init and kernel availability
and no implicit retrieval must be independently established before any launch.
No safe complete synthetic launch sequence can be issued while these gaps remain.
**Do not fill nulls by guessing, run the prefix, or approve runtime execution yet.**

## Prepare a fresh synthetic bundle (separate review/authorization)

After reviewing these files, authorize creation of **this new directory only**:

```sh
python3 -I -B qualification/apple_container.py prepare /private/tmp/faultline-apple-review-01
/usr/bin/shasum -a 256 /private/tmp/faultline-apple-review-01/evidence/prepared.json
```

Preparation runs no canary. It refuses an existing destination. There are no
dependencies beyond installed Python 3.10+ and its standard library. Do not
install Python under this procedure. Keep the printed receipt SHA-256 separately
on the trusted host; it is required for subsequent comparisons. The bundle has:

| Directory | Intended visibility in a later reviewed launch |
| --- | --- |
| `original` | Read-only at `/original`; synthetic source, selected tests and `.git` stand-in |
| `inputs` | Read-only at `/inputs`; fixed guest script, test copy, link probes, synthetic target paths |
| `private`, `unrelated` | No mount; synthetic tokens only |
| `protected` | No mount; synthetic protected receipt |
| `evidence` | Trusted host only; **never mounted**, copied into the guest, or writable by it |
| `/scratch` | Fresh, bounded guest-only writable storage for each control; no writable host bind |

The root or its parent must never be mounted. Neither the checkout, actual `.git`,
home, `/tmp`, keychain, SSH/cloud paths nor host/control/agent sockets may be
mounted. No inherited secrets, proxy variables, agents, privileged flags, extra
devices, host execution hooks or arbitrary entrypoint may be supplied. Pin the
image entrypoint explicitly to the reviewed interpreter and fixed guest fixture;
image startup hooks are execution too. The hard link deliberately shares the
synthetic source inode with `inputs/source-hardlink`; both visible paths must be
read-only. A read-only root alone is insufficient. The symlink to a private
synthetic host path tests namespace separation without disclosing real secrets.

Source hashes cover both collectors, this protocol, the old receipts, advice-only
skill and frozen #10 design. Each protected tree manifest records SHA-256, file
kind, path, modes, link targets, inode/device and hard-link count. It does not
follow symlinks or open sockets/devices. It rejects over 64 entries, depth over
eight, and files over one MiB. These are observer budgets for tiny fixtures,
not worker resource enforcement. Stable fixtures are required during observation.

## Runtime authorization sheet — BLOCKED, do not execute yet

Before requesting approval, fill in **concrete values**, review them, and retain
the sheet and its hash outside guest access. Approval must identify its exact
bytes. This preparation PR does not ask for blanket execution approval.

| Required item | Current state |
| --- | --- |
| Host label, normal-Terminal OS/build, architecture, virtualization capacity | Operator-provided Terminal report: macOS 27.0.1 / 26A434, arm64; no hardware attestation or capacity verification |
| Installed CLI version/path/hash and matched docs commit/content hashes | Reported 1.5.0 / d265d66 and executable SHA-256 retained; version-matched source review complete; binary/helper provenance not independently verified |
| Existing image by immutable digest, Linux arm64 interpreter/version, init/kernel digests | UNAVAILABLE; no image selected or retrieved |
| Exact setup argv and effects | NOT AUTHORIZED; no setup needed merely to prepare fixtures |
| Exact launch/inspect/stop/delete argv, cwd, explicit entrypoint, allowlisted environment | Help-matched candidate arrays retained in review record; complete launch BLOCKED by missing artifacts, environment, enforcement and observers |
| Enforced network denial including host routes, CPU/memory/PID/storage/output/wall limits | UNAVAILABLE; do not assume similarly named Docker flags exist |
| Independent network and VM/process observers with calibrated positive controls | UNAVAILABLE |
| Exact finite inert sink IPs/ports/protocols, capture interfaces and scope | NOT SELECTED; no production/public test destination or broad capture |
| Exact owned VM/container identities, termination and interruption recovery commands | Candidate identity-scoped stop/delete syntax reviewed; actual owned VM/helper identities and recovery observations missing |
| Working directories | Inspection/preparation/host verification: `/Users/grove/projects/faultline`; candidate runtime CLI cwd `/`, guest `/scratch`; observer cwd missing |
| Expected filesystem effects | Read only `original`/`inputs`; write only fresh guest scratch; host collector alone writes evidence. Setup may persist images/kernel/init separately; no writable host bind |
| Expected network effects | No worker external or host-facing traffic permitted; only separately approved calibration markers at exact inert sinks. Setup downloads are a different permission |
| Enforced resource budgets | Proposed: one VM/CPU, 256 MiB memory, 16 PIDs, 16 MiB scratch, 64 KiB output, 10 s/control, 360 s/session; enforcement UNAVAILABLE |
| Evidence/log destinations for first positive attempt | Proposed host-only `/private/tmp/faultline-apple-review-01/evidence/`: `prepared.json`, `positive.json`, `authorization.txt`, `cli.stdout`, `cli.stderr`, `host-observer.json`, `network-observer.json`; use exclusive creation and a fresh bundle for every later control |
| Exact cleanup commands and recovery | UNAVAILABLE; no approved runtime identities/stop/delete semantics yet. Do not launch until exact normal/timeout/interruption cleanup commands and host observations are reviewed |

This is a **blocked authorization sheet**, not an executable command sequence or
a request for synthetic execution approval. Installed client/help and matching
sources are recorded; image/init/kernel identities, independent denial observers,
enforced limits and demonstrated cleanup remain missing. **UNAVAILABLE / NO_GO**
applies even to positive startup. The smallest next authorization is only the two
fixture-preparation/hash commands above, not any runtime operation. No bundle has
been created at that named destination by this work.

Keep these permissions separate; approval must name exact commands and effects:

| Permission | Current authority |
| --- | --- |
| Normal-Terminal client inspection and preparation review/tests | Inspection supplied and reviewed; preparation/observer unit checks allowed; creation of the named operator bundle still awaits separate approval |
| Software installation or upgrade | NOT AUTHORIZED; require exact version/source/destination and install effects |
| Image/kernel/init downloads | NOT AUTHORIZED; require source, independently verified digest, destination, network/storage effects |
| Container service startup | NOT AUTHORIZED; require exact command, persistent service effects and any implicit downloads |
| Synthetic startup, adverse controls, observers/sinks and cleanup | NOT AUTHORIZED; require completed sheet, reviewed enforcement and exact scoped commands |
| Later Faultline/project/#10 challenges | NOT AUTHORIZED; separate task after qualification and independent review |

Service startup may fetch kernel/init artifacts. Image retrieval is network access
and persistent storage. They each require separately approved exact commands,
artifact identities, destinations and effects. An existing installation or a past
smoke attempt authorizes neither. An image tag is not a digest. Do not run a
guest to discover missing prerequisites, and do not add a custom firewall,
sandbox service, alternative runtime or dependency to fill a missing property.
If Apple Container cannot enforce any required limit or network prohibition on
this version, record **UNAVAILABLE / NO_GO** and stop qualification there.

## Control sequence and independent observations

One fresh bundle and new guest scratch/VM per attempt. Run the positive control
first, then exactly one adverse operation per attempt. Stop on drift, an allowed
forbidden effect, failed positive, missing telemetry, or cleanup uncertainty.
The guest filesystem action is the final argument to the fixed interpreter/script
argv after version review; it is **not** a host Python command. Never run
`apple_container_guest.py` on the host. It accepts only the fixed action names;
missing inputs/actions fail instead of executing a supplied command.

| Control | Fixture/action and required independent observation |
| --- | --- |
| Positive start/read/write | `positive`: exact source/test reads and scratch marker. Trusted runtime startup/process observation plus host extraction of the exact marker from the owned disposable guest, then inspect mount identities. Guest stdout alone cannot prove this. Extraction command pending version review. |
| Protected source/tests | `source-write`, `test-write`, `source-rename`: write or rename on read-only mount. Require trusted actual mount configuration, independent filesystem denial event tied to the operation, and unchanged manifest after each. Guest errno alone is diagnostic. |
| Protected receipt / private / unrelated | `receipt-write`, `private-read`, `unrelated-read`: attempt only generated synthetic absolute paths; no parent mount. Require host mount inventory/namespace evidence and a calibrated independent observer of attempted access. ENOENT and unchanged bytes alone do not demonstrate access denial or absence of a read. |
| Alias/path escapes | `symlink-write`, `symlink-read`, `hardlink-write`, `dotdot-write`, `root-write`: read/write fixed aliases and read-only guest root. Inspect actual resolved mount/inode identities and independent denial events, not just link spelling. |
| External TCP/UDP IPv4/IPv6 | Separate inert authorized endpoints for each protocol/family. First prove each sink and observer sees a permitted synthetic marker on the **same path**, then test denied traffic with capture and enforced-policy evidence. No observed packets by itself is insufficient. Not implemented: endpoints, policy and observer unavailable. |
| DNS TCP/UDP | Authorized inert resolver and calibrated observer; verify packets and policy independently, including direct-IP bypass tests. Empty resolver config is insufficient. Not implemented. |
| Host-facing TCP/UDP IPv4/IPv6 and Unix socket | Exact authorized host/gateway/host-only/proxy endpoints with calibrated sinks; no host service that executes guest requests. Test a synthetic socket only; verify no forwarded control sockets. `internal`/host-only networking cannot satisfy denial. Not implemented. |
| Memory / CPU / PIDs / output / storage | Independently inspect enforced aggregate caps **before** a bounded exceedance. Proposed ceiling: one VM, one CPU, 256 MiB memory, 16 PIDs, 16 MiB writable storage, 64 KiB output, 10 s/control, 360 s/session, at most 33 controls. Do not stress if any cap is absent; a guest self-limit or cooperative workload is insufficient. Proposed values are not installed flags or evidence. Not implemented. |
| Normal descendants | At most two synthetic children, one detached via setsid/double fork, finite 5 s sleeps. Independently map owned VM/helper identities before/after normal termination. No `ps` inside the guest as sole observer. Not implemented. |
| Timeout / interrupt / cleanup | Same bounded descendants with host deadline and an interrupted coordinator. Independently observe owned VM/helpers exit and no descendants/resources remain; preserve authoritative evidence. Killing the CLI process group or deleting metadata is insufficient. No arbitrary descendant stress or host-wide kill. Not implemented. |

The protected fixture manifest is **an implemented trusted host observation**:
after the guest has stopped and before the next control, substitute the separately
retained hash from preparation in this command (example action name only):

```sh
python3 -I -B qualification/apple_container.py verify /private/tmp/faultline-apple-review-01 positive --expected-prepared-sha256 RETAINED_SHA256
```

It creates a new exclusive `evidence/positive.json`; repeat with the relevant
fixed action name and a fresh bundle. A changed protected/source manifest gives
`NO_GO` and exit 1. Receipt substitution or missing/unreadable state aborts with
nonzero exit; retain that error as UNAVAILABLE, never GO. Successful comparison
gives **UNAVAILABLE**, not a denial or qualification. Compare retained evidence
hashes independently too; do not trust a baseline digest read from the same mutable
receipt. Before/after hashes cannot detect transient write/restore or private
reads; an unavailable independent denial observer blocks those controls.

Do not recursively delete a guest-controlled path or follow its links. This tool
does no cleanup. Keep bundles until independently reviewed, then approve exact
identity-scoped removal commands separately. Never remove all images, networks,
VMs, caches or unrelated services. A failed cleanup must retain evidence and block
the next run. The eventual operator sheet must include recovery after SIGINT,
SIGTERM, coordinator death and observation failure before any launch is approved.

## Decisions and validation in this PR

Review of the retained receipts establishes only: twelve historical native
launch failures before child startup; a later missing-CLI prerequisite inspection;
and a preparation inspection with `cli: null` and all 33 controls `NOT_RUN`.
Those historical receipts contain neither normal-Terminal CLI version/help nor
successful startup. The new operator-provided inspection adds client identity/help
only; its separate review adds pinned documentation and blocked argv. Neither
adds runtime evidence. The filesystem fixture and host manifest observer are
implemented; network, resource, descendant and cleanup probes are not. Retained
receipt source hashes identify their historical sources, not subsequent edits.

**GO FOR THE EXACT SYNTHETIC SCOPE** requires every required protection, successful
positive controls, independently observed denials/limits/descendant cleanup, intact
originals and protected evidence, complete provenance and independent review.
**NO_GO** records an observed prohibited effect, drift or failed control.
**UNAVAILABLE** records unrun controls, missing prerequisites or ambiguous evidence;
it blocks execution just as NO_GO does. Guest reports cannot promote either to GO.
The preparation tool deliberately has no GO path or external-result importer.

Maintainer tests exercise only fixture preparation, manifest comparison, receipt
integrity and syntax. They do not launch a canary, runtime, sink, sleeper or guest.
Installed-CLI inspection checks mock every subprocess call: they verify the exact
version/help-only argv, closed stdin, minimal environment, timeouts, retained-output
cap and failure reporting. Even successful mocked help retains `UNAVAILABLE` and
all controls `NOT_RUN`; these checks provide no installed-CLI or host safety evidence.
Use `python3 -I -B -m unittest discover -s tests -p test_apple_container.py -v`.
The existing full suite includes a host sleeper; do not run that test under the
current no-canary authority. No #10 code, project tests or skill execution is
enabled. Even eventual synthetic GO would not authorize any of those effects.
