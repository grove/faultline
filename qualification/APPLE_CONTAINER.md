# Apple Container qualification preparation — NOT RUN

Related to [#2](https://github.com/grove/faultline/issues/2); keep it open.
**Decision: UNAVAILABLE; execution NO_GO.** This is a preparation harness and
review procedure, not a qualified runner. It has no container-launch command,
GO override, installation, image retrieval, service startup or automatic cleanup.
Only the fixed filesystem fixture is implemented. Network, resource and lifetime
controls are specified below and remain unavailable, not passing placeholders.

The operator reports installing Apple Container and attempting a Terminal smoke
test. The version, command and outcome have **not** been observed here. Both the
session lookup and an explicitly requested host-shell lookup found no CLI on PATH
or at `/usr/local/bin/container`, `/opt/homebrew/bin/container`, `/usr/bin/container`.
The normal Terminal UI (iTerm2) is blocked by the computer-use tool's safety policy.
No alternative UI or weakened Codex boundary was used to bypass that block.
This bounded lookup does not disprove the operator's installation on another
host/context. The historical receipts are preserved unchanged.

## First Terminal evidence: client inspection only

From the reviewed Faultline checkout, in the normal macOS Terminal, review and
authorize this exact command. It reads host/CLI identity and client help, writes
nothing, and does not contact the container service:

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

Use the **observed** release version to select Apple's tagged command reference,
release notes and corresponding Containerization dependency, then pin their commit
and content hashes. Do not substitute `main` or the latest release. The references
are not version-matched until that comparison has actually happened. Also review
the installed `run`, `inspect`, `stop`, `delete`, and `image inspect` help captured
by the tool. Record discrepancies as blockers. No runtime flags are asserted in
this change: inventing a launch command before obtaining that version would make
the protocol misleading.

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
| Host label, normal-Terminal OS/build, architecture, virtualization capacity | Terminal evidence pending; Codex observations are a different context |
| Installed CLI version/path/hash and matched docs commit/content hashes | UNAVAILABLE |
| Existing image by immutable digest, Linux arm64 interpreter/version, init/kernel digests | UNAVAILABLE; no image selected or retrieved |
| Exact setup argv and effects | NOT AUTHORIZED; no setup needed merely to prepare fixtures |
| Exact launch/inspect/stop/delete argv, cwd, explicit entrypoint, allowlisted environment | BLOCKED pending installed help and enforcement review |
| Enforced network denial including host routes, CPU/memory/PID/storage/output/wall limits | UNAVAILABLE; do not assume similarly named Docker flags exist |
| Independent network and VM/process observers with calibrated positive controls | UNAVAILABLE |
| Exact finite inert sink IPs/ports/protocols, capture interfaces and scope | NOT SELECTED; no production/public test destination or broad capture |
| Exact owned VM/container identities, termination and interruption recovery commands | BLOCKED pending runtime version; never delete by name pattern or all-containers flags |

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

**GO FOR THE EXACT SYNTHETIC SCOPE** requires every required protection, successful
positive controls, independently observed denials/limits/descendant cleanup, intact
originals and protected evidence, complete provenance and independent review.
**NO_GO** records an observed prohibited effect, drift or failed control.
**UNAVAILABLE** records unrun controls, missing prerequisites or ambiguous evidence;
it blocks execution just as NO_GO does. Guest reports cannot promote either to GO.
The preparation tool deliberately has no GO path or external-result importer.

Maintainer tests exercise only fixture preparation, manifest comparison, receipt
integrity and syntax. They do not launch a canary, runtime, sink, sleeper or guest.
Use `python3 -I -B -m unittest discover -s tests -p test_apple_container.py -v`.
The existing full suite includes a host sleeper; do not run that test under the
current no-canary authority. No #10 code, project tests or skill execution is
enabled. Even eventual synthetic GO would not authorize any of those effects.
