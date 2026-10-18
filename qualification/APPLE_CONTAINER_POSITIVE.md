# Positive Apple Container smoke review — BLOCKED / NOT RUN

**Current next request:** [identity-scoped setup-v2 recovery](APPLE_CONTAINER_RECOVERY.md).
The authorized setup-v2 attempt started four services in `user/501`; Faultline
rejected trailing-slash paths and could not complete recovery. Services may
remain active. The original receipt is preserved; no VM or canary ran.
No further startup, provisioning or execution is authorized.

The historical preparation and setup proposals below are retained as context.
All prerequisite checks and Stage 1a are complete; do not repeat them or reuse
any consumed attempt identity.

Latest supplement for draft [PR #17](https://github.com/grove/faultline/pull/17)
and [issue #2](https://github.com/grove/faultline/issues/2). **Execution NO_GO;
qualification UNAVAILABLE.** No VM or canary has been launched; read-only host observations are recorded separately.
This document does not authorize setup, execution, a budget change or cleanup.

## Preparation verified

The operator ran preparation at `/private/tmp/faultline-apple-review-01`.
The independently retained SHA-256 is
`3349e3c1e401afa9c32de55ecd385cd65afc46b01fcfbb7660d1c0f763f4426d`.
The visible receipt matches that hash; a
[byte-for-byte copy](2026-10-18-apple-container-prepared.json) is retained here.
All eight current source hashes and all five protected-tree manifests match it.
The original evidence directory contains only `prepared.json`; all 33 runtime
controls are `NOT_RUN`. This is preparation evidence, not startup or denial evidence.

The prepared receipt hashes `APPLE_CONTAINER.md`, the collectors and guest fixture.
Those files remain unchanged to preserve this baseline. Their earlier preparation
instructions are historical; **do not rerun preparation over the existing directory**.
The receipt's generic hardcoded version-review blocker is preserved literally;
the [separate version review](2026-10-18-apple-container-review.json) records the
completed source review without rewriting the receipt.

## Exact candidate image and positive operation

Proposed worker image, pinned to the **Linux arm64/v8 platform manifest**:

```text
docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d
```

Discovery used Docker Official Python's `3.13-slim-bookworm` tag metadata, followed
by digest-addressed registry manifest/configuration GETs. Both content hashes were
verified. The configuration digest is
`sha256:da841a7026abc0089180121604f6d0ba4324998e2d133eccae13f22707055dc1`;
it records Python 3.13.16, no entrypoint, default command `python3`, no declared
volumes and four public image environment values. See the
[positive review record](2026-10-18-apple-container-positive-review.json) for raw
manifest descriptors, exact image environment and source/content provenance.
No layer payload was fetched. Metadata does not verify publisher build provenance,
local presence or the interpreter file. The proposed explicit interpreter path
`/usr/local/bin/python3` still needs offline filesystem verification after separately
authorized provisioning; a tag, config value or Dockerfile is not that verification.

The smallest guest operation reuses the prepared, fixed `positive` action:

```text
/usr/local/bin/python3 -I -S -B /inputs/guest.py positive
```

It reads the exact synthetic source/test bytes and writes
`synthetic-approved-output\n` to `/scratch/output.txt`, then returns. No adverse
control, project import, test discovery, shell, network attempt or child stress is
part of this scope. Never execute that guest command on the host.

## Runtime, filesystem and network specification

The positive review JSON contains exact fixed argv components and the pinned
worker image. It deliberately has **no complete runnable launch sequence**:
`--init-image` digest, `--kernel` path/hash and host environment remain unresolved.
Do not concatenate its components or allow implicit default artifact selection.
Installed CLI SHA-256 was independently read and matches the operator's earlier
report. Strict signature verification failed in the restricted Codex context;
the later operator-provided normal-Terminal output reports valid code under Apple's
certificate chain. Preserve both observations; the restricted result is not evidence
of tampering. Neither result establishes runtime containment.

| Item | Proposed value and unresolved evidence |
| --- | --- |
| CLI / host cwd / owned name | `/usr/local/bin/container`; `/`; `faultline-apple-review-01-positive`. Verify no pre-existing identity and bind it to actual owned VM/helper identities before any effect. |
| Entrypoint / guest cwd / identity | `/usr/local/bin/python3`; `/scratch`; UID/GID 65534 with `--cap-drop ALL`. Interpreter and effective permissions/capabilities remain unverified. |
| Read-only root | `--read-only`; actual root mount must be independently inspected. |
| Source mount | `--mount type=virtiofs,source=/private/tmp/faultline-apple-review-01/original,target=/original,readonly` |
| Input mount | `--mount type=virtiofs,source=/private/tmp/faultline-apple-review-01/inputs,target=/inputs,readonly` |
| Scratch | `--tmpfs /scratch:size=16m,mode=0700,uid=65534,gid=65534`; guest-only and fresh. Default writable mounts are additional unresolved storage exposure. |
| Invisible host paths | No mount of `private`, `unrelated`, `protected`, `evidence`, their parent, checkout, real `.git`, home, credentials or host/control sockets. No writable host bind. |
| Network | `--network none --no-dns`; zero attachments in matching source. No publish, publish-socket, SSH, proxy or agent forwarding. Actual routes/interfaces/IPC and enforced denial remain unverified; no sink/probe is authorized. |
| Environment / descriptors | Image config values retained for review; no bare `--env`, env file or inherited secret/agent variables. Effective host/guest allowlists remain unverified. Closed stdin and unrelated descriptors required. |
| Artifacts | Worker manifest pinned remotely; local worker layers/interpreter, immutable vminit and actual kernel identities unavailable. `ClientImage.fetch` can pull on a cache miss. No service or artifact retrieval authorized. |

The documented default app root, `/Users/grove/Library/Application Support/com.apple.container`,
is absent in this session. The operator reports no custom app root. No daemon was
contacted to discover other state; local runtime readiness is **UNAVAILABLE**.

## Resource and independent-observation blockers

The earlier proposed ceiling remains one VM, one VM CPU, 256 MiB VM memory,
16 PIDs, 16 MiB total writable storage, 64 KiB output, 10 s/control and 360 s/session.
**No higher budget has been approved.** The matching `RuntimeService.swift` adds
one default overhead CPU and 128 MiB guest overhead: `--cpus 1 --memory 256M`
predicts a **2-vCPU / 384-MiB VM before memory alignment**, with separate workload
cgroup limits of one CPU / 256 MiB. It does not meet that proposed whole-VM ceiling.
Do not relabel workload limits as whole-VM limits or increase the ceiling to pass.
Aggregate PID, total writable storage, output and host-owned deadlines are also
unavailable; per-process rlimits do not fill those gaps.

| Independent observation required | Availability |
| --- | --- |
| Host-owned mapping from exact runtime identity to VM/helper processes, effective mounts, interfaces and caps | No reviewed exact observer command or collected evidence. CLI inspect alone does not establish all properties. |
| Calibrated external/host/Unix-socket network denial observer | No selected observer/endpoints or independent runtime-policy proof. No broad capture or public probe proposed. |
| Host-enforced aggregate limits, wall deadline and coordinator-death recovery | No reviewed mechanism or observer. Killing the CLI process group is insufficient. |
| Trusted extraction of the exact scratch marker | Not implemented. The fixed guest returns immediately after its tmpfs write; matching runtime exit handling tears down the VM. Post-exit copy/inspect cannot be assumed to recover tmpfs bytes. Guest stdout is insufficient. |
| Normal, timeout and interruption cleanup | Identity-scoped commands have matching syntax, but no independently observed VM/helper termination or recovery procedure. |

These are prerequisites, not passing placeholders. A cooperative tiny positive
does not remove the requirement for enforced containment. Do not build a new
sandbox engine, change the fixture or loosen controls to get startup evidence.

## Cleanup review — NOT AUTHORIZED

Exact candidate CLI argv, all with host cwd `/` and a separately reviewed environment:

```text
/usr/local/bin/container inspect faultline-apple-review-01-positive
/usr/local/bin/container stop --time 1 faultline-apple-review-01-positive
/usr/local/bin/container delete faultline-apple-review-01-positive
```

On normal exit, retain startup/marker/exit and independent VM/helper observations.
On timeout, SIGINT, SIGTERM or coordinator death, an independent host owner must
apply the scoped stop and prove termination; that owner/procedure is not yet
available. Delete metadata only after independently proving the exact owned
runtime has stopped. Matching runtime cleanup catches/logs stop errors and releases
waiters; stopped metadata alone does not prove VM termination. If termination or
observation fails, retain evidence, stop
the procedure and request recovery for that exact identity. No `--all`, `--force`,
auto-remove, process-name kill, image pruning or fixture deletion is proposed.

Only **after a real separately authorized positive attempt and independently
observed stop**, the exact host manifest comparison would be:

```text
python3 -I -B qualification/apple_container.py verify /private/tmp/faultline-apple-review-01 positive --expected-prepared-sha256 3349e3c1e401afa9c32de55ecd385cd65afc46b01fcfbb7660d1c0f763f4426d
```

Its cwd is `/Users/grove/projects/faultline`. It writes a new host-only
`evidence/positive.json` and remains UNAVAILABLE even if unchanged. It has not
been run: writing that control receipt now would misrepresent the stage.

## Approved prerequisite checks — operator completed

The user approved only the following three read-only checks. Computer-use access
to iTerm2 was denied for safety reasons; no UI or host-execution route bypassed
that denial. The operator then ran the approved commands directly and returned
their output. They invoke neither Container nor a service, download nothing and
launch no guest. **Do not ask for approval or run them again merely to repeat
this completed prerequisite collection.**

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/codesign --verify --strict --verbose=2 /usr/local/bin/container
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/codesign --display --verbose=4 /usr/local/bin/container
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /usr/sbin/sysctl hw.optional.arm64 hw.logicalcpu hw.memsize kern.hv_support
```

The [normal-Terminal transcript](2026-10-18-apple-container-terminal-prerequisites.json)
reports `valid on disk` and satisfaction of the Designated Requirement, with
Apple's Developer ID Application / Developer ID Certification Authority / Apple
Root CA chain and TeamIdentifier `UPBK2H6LZM`. The embedded CDHash matches the
earlier display. It reports arm64, **10 logical CPUs**, **34359738368 bytes
(32 GiB)** of RAM and `kern.hv_support: 1`. Numerical command exit statuses,
raw-file hash and run timestamp were not supplied; none is invented. The prompt
shows the Faultline checkout rather than requested cwd `/`; all approved commands
use absolute paths and no cwd-dependent inputs.

The same minimal-environment checks in the restricted session returned codesign exit 1 with
`invalid signature`, display exit 0 with authority unavailable, and sysctl exit 1
with `Operation not permitted`. These observations do not by themselves establish
tampering or failure in normal Terminal. No re-signing, quarantine removal,
security bypass, reinstall, setup or launch is authorized to resolve them.

The completed normal-Terminal checks resolve the reported signature/capacity
prerequisite uncertainty. They leave the artifact, VM-budget, aggregate-limit,
network, observer, marker-retention and cleanup blockers above. **There is no
positive-container execution authorization request ready yet.** Keep PR #17 draft,
issue #2 open and the Faultline skill advice-only.
