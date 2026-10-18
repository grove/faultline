# Next authorization: service inventory, then provisioning, then positive execution

For draft [PR #17](https://github.com/grove/faultline/pull/17) and open
[issue #2](https://github.com/grove/faultline/issues/2). **Nothing here grants
execution authority. No runtime command has been executed by this change.**
The completed signed-1.5.0 / Apple Silicon / 10-CPU / 32-GiB / virtualization
prerequisites are accepted. Do not repeat them. The old preparation bundle,
fixture, source hashes and receipts remain untouched.

## Approve this next: stage 1a, inventory only

Working directory: `/Users/grove/projects/faultline`. Exact command:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C /opt/homebrew/bin/python3 -I -B qualification/apple_container_smoke.py inventory /private/tmp/faultline-apple-positive-v2
```

This host helper runs **only** these two subprocesses, sequentially, each with
cwd `/`, closed stdin/unrelated descriptors, a 15-second timeout and exactly
`HOME=/Users/grove`, `PATH=/usr/bin:/bin`, `LC_ALL=C`:

```text
/usr/local/bin/container system status --format json
/usr/local/bin/container image list --format json
```

It exclusively creates `/private/tmp/faultline-apple-positive-v2/evidence/inventory.json`.
The first command must succeed, report a running server and report app root
`/Users/grove/Library/Application Support/com.apple.container`; otherwise stop
before the second. It then reads/hashes only the default kernel alias
`kernels/default.kernel-arm64`, allowing its resolved file only within that
same `kernels` directory. An image-list entry is cache metadata, **not** proof
that every blob or snapshot is complete. Missing metadata means retrieval is
needed; present metadata requires blob/snapshot verification before launch.

**Permission requested:** local XPC service contact, including launchd activation
of already registered API/image helpers, runtime-store metadata and kernel reads,
and that one new host evidence file. No `system start`, service registration,
installation, explicit artifact retrieval, VM, canary, external network request,
registry login or credential extraction. Services can persist their own normal
state/logs under the existing app root and macOS logging. Do not claim this is a
zero-side-effect filesystem inspection. No service is stopped automatically:
it may predate this attempt. If unregistered or unavailable, retain failure and
request stage 1b; do not fix it automatically or bypass Codex restrictions.

Timeout, nonzero exit, invalid status, different app root, kernel alias outside
the allowed store, a kernel over the 128-MiB read budget, or more than 64 KiB on
either retained stream stops inventory.
Partial timeout output is preserved. Capture is of trusted CLI metadata and is
bounded in time; 64 KiB is a retention bound, not a live subprocess output quota.
Review local image names/paths before publishing this evidence. Do not rerun
over the same evidence file. This is the **only approval requested now**.

## Artifact lock and stage 1b: separate provisioning approval

| Artifact | Immutable identity / availability before inventory |
| --- | --- |
| Installed client | Apple Container 1.5.0, source `d265d669ecae041bf338cb3b39c4118316d138f0`; previously recorded client SHA-256 `8cc619377e8978a0ce9f22a3e864dcd4445f2bc38fb64c5197bb69a1bab42463`. Accepted completed prerequisites; no recheck requested. |
| Python worker | `docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d`, Linux arm64/v8, Python 3.13.16. Manifest/config metadata previously hash-verified; config `sha256:da841a7026abc0089180121604f6d0ba4324998e2d133eccae13f22707055dc1`. Four compressed layers total 46,062,357 bytes; local completeness unknown. |
| Init | Locked Containerization 0.47.0, source `bc994b88df46207fad7775b0eabc51947e315881`; public Apple package lists arm64/v8 manifest `sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade`, parent index `sha256:4c1836052eafcbc944c403fb23ded06562962d2402c9dcc651495a32300614df`. Manifest bytes/blobs and local presence not yet verified. |
| Kernel | Kata 3.32.0 arm64 archive SHA-256 `8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5`; member `opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug`. Archive pin is supplied by Container 1.5.0 source. Installed extracted-binary hash unknown until inventory/provisioning; never substitute an arbitrary existing kernel. |
| Supporting artifacts | Existing signed runtime/API/image helpers and macOS Virtualization.framework; helper identity/configuration must be recorded from setup. Native arm64 needs no Rosetta, builder image, package installation, project dependency, network plugin attachment or downloaded Python package. Image/init EXT4 snapshots are additional persistent setup artifacts. |

Sources: [Apple init package version](https://github.com/apple/containerization/pkgs/container/containerization%2Fvminit/1291686959?tag=0.47.0),
[kernel/default-init configuration](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPersistence/ContainerSystemConfig.swift).
Availability is **unknown**, not missing merely because a restricted session did
not see a store. No artifact payload was retrieved in this follow-up.

These are the exact candidate retrieval commands for separately approved
stage 1b, using the same minimal environment and cwd `/` as stage 1a:

```sh
/usr/local/bin/container image pull --platform linux/arm64/v8 --progress plain --max-concurrent-downloads 1 docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d
/usr/local/bin/container image pull --platform linux/arm64/v8 --progress plain --max-concurrent-downloads 1 ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade
/usr/local/bin/container system kernel set --arch arm64 --tar https://github.com/kata-containers/kata-containers/releases/download/3.32.0/kata-static-3.32.0-arm64.tar.zst --binary opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug --digest sha256:8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5
```

Worker source: Docker Official Python via registry-1.docker.io/auth.docker.io and
registry blob redirects; init: ghcr.io and its blob redirects; kernel: GitHub
release assets and redirects. Host DNS/TLS/HTTPS is required for setup only.
No registry login, user-supplied credentials or insecure transport is proposed.
Runtime content is stored below the approved app root (content/images/snapshots);
kernel retrieval uses an OS-created temporary directory, then copies the member
to `kernels/vmlinux-6.18.35-197-debug` and updates `default.kernel-arm64`.
The kernel command changes the default kernel; stage 1b must explicitly approve
that effect or instead approve extraction to a dedicated path. No `--force`:
an existing destination is a stop, not permission to replace it.

Verification: retain digest-addressed manifest/config bytes and all blob sizes
and SHA-256 values; compare worker descriptors with the existing positive-review
JSON, and verify init manifest bytes against the package pin before accepting it.
Hash every local blob, including layers; verify complete platform snapshots.
Verify the kernel archive **before** extraction (the pinned KernelService does
this), then retain the extracted binary SHA-256 and archive/member provenance.
Inspect interpreter/symlink files offline in the verified image; do not run an
image to discover Python. Pin that resulting kernel path/hash in stage 2.
Retain setup argv, exit status, raw logs and hashes under this bundle's evidence
directory, never mounted into the VM. A digest mismatch, authentication prompt,
unreviewed redirect/effect, incomplete blob/snapshot or failed command stops setup.

**Do not approve service startup as a harmless offline step.**
[SystemStart.swift](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStart.swift)
pulls a missing configured init even with `--disable-kernel-install`. If startup
is necessary, candidate `/usr/local/bin/container system start --disable-kernel-install --timeout 15`
requires a separate exact configuration/startup approval: it registers persistent
launchd services, creates app-root state, and may retrieve init. The configured
init must first be bound to the reviewed immutable reference; a mutable default
tag is insufficient. Do not execute this candidate with unresolved configuration.

[SnapshotStore.swift](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/ContainerImagesService/Server/SnapshotStore.swift)
uses host EXT4 unpacking. Its default virtual capacities are 512 MiB for the
**configured reference** to init and 512 GiB otherwise; a different digest-spelled
alias can take the latter path. These are sparse virtual capacities, not measured
host disk use or scratch quotas. Provisioning must record physical/logical sizes,
pin the effective init configuration and explicitly bound host storage before
unpacking. No unpack/start is authorized by this document. Inventory is needed
before selecting a safe bounded setup, rather than assuming a 16-MiB scratch flag
caps the image store.

## Budget proposal for stage 2 — not yet approved

| Scope | Proposed explicit limit |
| --- | --- |
| VM | One VM, ceiling **2 vCPUs / 512 MiB guest RAM**. No silent change to earlier authority. |
| Workload | Retain **1 CPU / 256 MiB**: `--cpus 1 --memory 256M`. CPU cgroup quota 100000/100000 microseconds; memory cgroup limit 268435456 bytes. |
| Actual source-predicted VM allocation | **2 vCPUs / 384 MiB**, including one overhead CPU and 128 MiB for kernel/init. It fits the proposed ceiling; the remaining 128 MiB is not allocated extra headroom. |
| Process | One fixed nonforking Python process; `--ulimit cpu=2 --ulimit nproc=16 --ulimit nofile=32 --ulimit fsize=4096 --ulimit core=0`. These are per-process/UID rlimits, not an aggregate PID policy. |
| Guest writable storage | Fresh `/scratch` tmpfs 16 MiB; `/dev/shm` 1 MiB. Default runtime tmpfs/dev mounts remain additional, contained in finite VM memory; **16 MiB is not a total writable-storage limit**. No writable host bind or image-declared volumes. |
| Time/output | Guest alarm 8 s; proposed host VM deadline 10 s from bootstrap, plus 5 s cleanup; total stage-2 session 60 s. Host must count/drain CLI output, stop at 64 KiB combined and bound its retained runtime logs. Fixed fixture emits no stdout/stderr on success and writes a 26-byte marker. |

[RuntimeService](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/RuntimeLinux/Server/RuntimeService.swift)
adds overhead separately from the workload;
[LinuxContainer](https://github.com/apple/containerization/blob/bc994b88df46207fad7775b0eabc51947e315881/Sources/Containerization/LinuxContainer.swift)
sets the cgroup CPU/memory limits.
[VZVirtualMachineInstance](https://github.com/apple/containerization/blob/bc994b88df46207fad7775b0eabc51947e315881/Sources/Containerization/VZVirtualMachineInstance.swift)
rounds memory to one MiB: 384 MiB stays 384 MiB. This is a source prediction,
not observed installed enforcement. The default overhead is a reasonable first
tiny-process candidate, not a measured boot guarantee. OOM/boot failure stops;
no automatic increase to 512 MiB workload. The VM RAM ceiling excludes host VMM,
API/image helpers and filesystem cache; it is not a 512-MiB total-host-RSS promise.

## Positive v2: marker collection before teardown

New frozen [guest](apple_container_positive_v2.py) and host-only
[preparation/inventory helper](apple_container_smoke.py). Preparation creates
`/private/tmp/faultline-apple-positive-v2` once, with only synthetic `original`,
`inputs` and host-only `evidence`. Its `prepared-v2.json` records new source/tree
hashes and links the historical prepared receipt hash without rewriting it.
Guest code is syntax-checked only during development; never run it on the host.
The frozen guest SHA-256 is
`bb20d238a7834551147efc6f3e15fc3ea56f844a5c506ad6aeaa2a0ffb752412`.

The v2 guest verifies the same two fixed inputs, exclusively writes and fsyncs
`synthetic-approved-output\n` at `/scratch/output.txt`, then waits for the exact
stdin line `faultline-positive-v2-ok\n`. Its eight-second alarm covers reads,
write and wait. EOF/wrong input fails; missing acknowledgement terminates it.
There are no project imports, discovery, subprocesses, network operations or
negative actions. Use `--interactive` without TTY for the host-owned stdin pipe.

While the VM is still running, the proposed trusted host observer issues:

```text
/usr/local/bin/container cp faultline-apple-positive-v2:/scratch/output.txt /private/tmp/faultline-apple-positive-v2/evidence/marker.txt
```

Require an absent destination, successful copy, a regular nonsymlink file, exact
26 bytes and SHA-256
`ea836bec0f77416318e6411cb739e48fae78af54b66c9d1e1156c612a8ca394e`.
Record the
copy's argv/time/status and the host-read bytes/hash; only then send the fixed
acknowledgement and close stdin. A bounded retry within the same deadline can
handle the file not existing yet; never reset the deadline. Failed/missing copy
means failure even if stdout looks successful. No writable host mount is needed.
The [runtime copyOut route](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/RuntimeLinux/Server/RuntimeService.swift)
accepts running/booted VMs; post-exit tmpfs retrieval is not viable. This observes
actual file bytes across the runtime control channel, independently of fixture
stdout; it does not attest an uncompromised guest kernel or prove network denial.

The future exact launch uses owned name `faultline-apple-positive-v2`, cwd `/`,
the stage-1a host environment, closed unrelated descriptors, and these fixed flags
plus the **verified setup kernel path** (unresolved, so this is not a runnable command):

```text
run --name faultline-apple-positive-v2 --arch arm64 --os linux
--read-only --network none --no-dns --interactive
--mount type=virtiofs,source=/private/tmp/faultline-apple-positive-v2/original,target=/original,readonly
--mount type=virtiofs,source=/private/tmp/faultline-apple-positive-v2/inputs,target=/inputs,readonly
--tmpfs /scratch:size=16m,mode=0700,uid=65534,gid=65534 --shm-size 1M
--uid 65534 --gid 65534 --cap-drop ALL --cpus 1 --memory 256M
--ulimit cpu=2 --ulimit nproc=16 --ulimit nofile=32 --ulimit fsize=4096 --ulimit core=0
--workdir /scratch --entrypoint /usr/local/bin/python3
--init-image ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade
--kernel [verified-setup-path]
docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d
-I -S -B /inputs/positive-v2.py positive-v2
```

The image's four reviewed public environment values are retained from the
positive-review JSON; no bare `--env`, env file, host credentials or agent/proxy
variables. Guest UID/GID must be able to read the two synthetic mounts. No parent,
checkout, real `.git`, home, private directory, evidence, host/control socket,
publish flag, SSH forwarding, Rosetta, nested virtualization or additional device.
No network attachment is requested; privileged runtime vsock/virtiofs control
channels still exist. No negative network probe is included.

## Cleanup gate and stage 3

Before stage 2 can be offered for approval, a host-owned guardian must survive
coordinator death, own the fixed deadline, bind the fresh container to its exact
launchd runtime service/PID/start identity, and retain independent observations.
It must be armed **before bootstrap**, check that the name did not preexist, and
have authority to terminate precisely that VM owner even if XPC stop hangs.
Candidate normal/timeout/interrupt cleanup commands are:

```text
/usr/local/bin/container stop --time 1 faultline-apple-positive-v2
/usr/local/bin/container inspect faultline-apple-positive-v2
/usr/local/bin/container delete faultline-apple-positive-v2
```

Retain start/configuration, marker, exit status, monotonic timings, guardian
actions and pre/post protected manifests under `evidence/`. Confirm the owned
VM/runtime PID is gone using the independent host identity observer **before**
deleting metadata. Never use `--all`, global service stop, name-based process
kill, force delete, image pruning or removal of receipts. On uncertain ownership
or cleanup, stop and retain state for exact-identity recovery; no next attempt.

**Exact remaining mechanism:** no separately supervised guardian or verified
runtime-service-to-PID mapping/fallback termination is installed/reviewed in this
PR. The helper's source label is `com.apple.container.runtime.container-runtime-linux.<uuid>`;
do not assume the UUID equals the chosen CLI name without setup evidence.
CLI inspect/stopped metadata and killing the launching process group cannot
substitute for this mechanism. Host disk/log bounds and complete cached artifacts
also need setup evidence. Therefore **positive execution remains blocked**, even
though marker synchronization and the budget calculation are now resolved.

For the limited positive test, exact trusted nonforking fixture bytes, verified
artifact/configuration, read-only synthetic shares, no network attachments,
finite VM/process limits, bounded host collection and independent lifetime cleanup
are minimum requirements. Calibrated adversarial network/file/PID/descendant
denial proofs are **not** required to call that one positive test successful.
Stage 3 requires a fresh bundle and a separate exact authorization for existing
negative fixture actions and calibrated observers; no negative command is
authorized by stage 1 or 2. Aggregate PID/storage/output enforcement, external/
host/Unix-socket isolation and normal/timeout/interruption/death recovery remain
full execution-safety qualification requirements. A positive result is only
**SYNTHETIC_POSITIVE_OBSERVED**, never sandbox qualification or authority for
the advice-only skill, target projects or experiment #10.
