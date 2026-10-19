# Setup-v4 — one fresh service/startup and pinned-init provisioning proposal

**PREPARED ONLY. Requires separate approval.** Keep PR #17 draft, issue #2 open,
Faultline execution **NO_GO / UNAVAILABLE**. No new startup, image retrieval,
cleanup, VM, canary, worker/kernel provisioning or #10 was executed to prepare this.
All earlier attempt/recovery authorizations are consumed; preserve their receipts
and directories. This proposal changes only the existing setup helper and its
tests, plus the current proposal/outcome documentation. It adds no runner/framework.

## What setup-v3 established

The [original receipt copied byte for byte](2026-10-19-apple-container-setup-v3.json)
matches the unchanged operator file
`/private/tmp/faultline-apple-positive-v2/evidence/setup-v3.json`, SHA-256
`27d50d2a34e6fc12c30066068b5edc754ad545bf34004cd1b781827c4ad644e1`.
It records reviewed script/config/observer hashes, startup exit 0, running 1.5.0
and correct full commit/roots. Recovery verified the four service/process identities;
exact-init inspection returned 1, image not found. Four exact bootouts returned 0;
final scoped services/Mach endpoints/processes/DNS listeners were empty.
Result **FAILED**, recovery **SCOPED_RECOVERY_OBSERVED**. Setup-v3 is consumed.
These are receipt observations; Codex did not witness or repeat the operator's run.

The [six-second read-only startup log observation](2026-10-19-apple-container-setup-v3-startup-logs.json)
covers 2026-10-19 09:12:44–09:12:50 Europe/Oslo, the four recorded service PIDs and
Container CLI, with the Container subsystem retained. It records helper startup,
NAT creation and DNS startup, and missing default kernel (installation was disabled).
It contains no init retrieval error. The receipt's CLI stderr has neither
`Installing base container filesystem...` nor the internal pull-error message.
Log absence alone does not establish whether network traffic occurred.

Pinned source supplies a narrower explanation, **inferred, not a captured exception**:

- [SystemStart at Container 1.5.0](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStart.swift)
  calls `try? await installInitialFilesystem(...)`. That function first calls
  `ImagePull.parse()`, before setting `reference` or logging installation. Its later
  catch also logs retrieval errors without propagating them.
- [Locked ArgumentParser 1.8.2](https://github.com/apple/swift-argument-parser/blob/6a52f3251125d74daf04fcbd5e6f08a75d074382/Sources/ArgumentParser/Parsable%20Types/ParsableArguments.swift)
  defines `parse(nil)` as parsing the program's command-line arguments.
  Thus it reparses `system start --app-root ... --install-root ...
  --disable-kernel-install --timeout 15` as
  [ImagePull](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/Image/ImagePull.swift),
  whose options do not accept those startup flags or positional arguments. The
  outer `try?` suppresses this pre-retrieval error. This explains the observed
  missing installation log without assigning a registry/network cause.
- [ImageInspect](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/Image/ImageInspect.swift)
  looks up the image, then deliberately filters the configured init from output.
  A missing image yields exit 1; an installed configured init can yield exit 0 and
  `[]`. Setup-v3's nonempty-result requirement would incorrectly reject that case.

There is no evidence here establishing networking, authentication, unsupported
digest syntax or cache failure. No registry probes, login attempts, alternate
digests/tags or upgrades are proposed. No additional diagnostics are needed before
this request: the explicit pull below will retain its own actual exit/error.
If that fails, preserve its receipt/root and review the exact recorded failure;
do not infer a cause, retry or add diagnostic network requests. A later diagnostic
request can limit unified-log reads to the receipt's start/end times and captured
PIDs, 30 s query timeout and 1 MiB capture, without any service/client activation.

## Exact approval requested

Approve **one** operator-Terminal execution in `/Users/grove/projects/faultline`:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B qualification/apple_container_service_setup.py setup-v4
```

Required SHA-256 identities (do not substitute changed bytes):

```text
82a20ecffdedef478b72fe4b3b9a384cb8e35ad9b407b7e61c510a596b21f101  qualification/apple_container_service_setup.py
c86e1c77332d4d9bb8785c5136dedbf1d258a2aba0623a2d9d38e78c9317b6a0  qualification/apple_container_recover_setup_v2.py
ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e  qualification/apple-container-service.toml
```

The [preparation manifest](2026-10-19-apple-container-setup-v4-review.json) pins all
installed CLI/service/plugin identities and exact effects. Use only Container
**1.5.0 / d265d669ecae041bf338cb3b39c4118316d138f0**, locked Containerization
**0.47.0 / bc994b88df46207fad7775b0eabc51947e315881**. No software build/install
or version substitution. Completed signature/hardware prerequisites are accepted;
fresh software hashes and collision checks guard only this attempt.

Exclusively create `evidence/setup-v4.json` and a new mode-0700 `setup-v4` beneath
`/private/tmp/faultline-apple-positive-v2`. Any existing receipt/directory stops the
attempt. No reuse, overwrite, prune or deletion of prior state. The consumed
setup-v3 helper bytes remain in [immutable PR history](https://github.com/grove/faultline/blob/3b25cd281d75be12a013c4f5dbfd66324403ce69/qualification/apple_container_service_setup.py),
SHA `465c1d999a5bf0566f0994834d04b18bb2a96b41ebb6d48a2e940eb829e9f1ec`.
The updated entrypoint accepts only `setup-v4`.

All child commands have cwd `/`, closed stdin/unrelated descriptors and exactly:

```text
HOME=/Users/grove
PATH=/usr/bin:/bin
LC_ALL=C
TZ=Europe/Oslo
XDG_CONFIG_HOME=/private/tmp/faultline-apple-positive-v2/setup-v4/config-home
CONTAINER_APP_ROOT=/private/tmp/faultline-apple-positive-v2/setup-v4/runtime
CONTAINER_INSTALL_ROOT=/usr/local
```

The sequence is mandatory; the pull is **not** a standalone command for the
recovered/stopped setup-v3 system:

1. Reuse the existing source/binary/plugin guards, manager selection and
   system/user/GUI service/Mach-endpoint, targeted process and DNS-listener baseline
   observations. Any collision, ambiguity, changed/custom software or unsupported
   session blocks startup. Keep all other Container management idle.
2. Copy the unchanged pinned TOML to fresh private config. Require at least 2 GiB
   free and at most 1 GiB logical/allocated attempt storage. Then run once:

   ```text
   /usr/local/bin/container system start --app-root /private/tmp/faultline-apple-positive-v2/setup-v4/runtime --install-root /usr/local --disable-kernel-install --timeout 15
   ```

   Startup may itself attempt implicit init retrieval; that possibility remains
   inside the approved download/network scope, but its success is never trusted.
3. Check running service status, full version/commit, app/install filesystem roots,
   copied config bytes and all four exact service/Mach identities. Freeze PID,
   UID, executable hash, birth and owned plist identities using the existing
   observer. Check storage/free space again. Only then run **one explicit pull**:

   ```text
   /usr/local/bin/container image pull --platform linux/arm64/v8 --scheme https --progress plain --max-concurrent-downloads 1 ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade
   ```

   [ImagePull](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/Image/ImagePull.swift)
   calls the registered image helper over XPC, pulls and unpacks, and propagates
   failures. Reserve/checkpoint the receipt before the pull; retain exit, timeout
   and partial stdout/stderr. No automatic retry. Kernel installation stays disabled.
4. Check storage/free space. Require exact-init `image inspect` exit 0 (empty array
   is allowed), then inspect only this fresh runtime offline:
   `state.json` must contain exactly the intended reference and a hash-verified
   synthetic single-platform index. Its descriptor must reference the pinned
   manifest. Hash that manifest, its config and **every layer**, comparing exact
   descriptor sizes/SHA-256. Require linux/arm64/v8, accepting omitted arm64 variant
   as v8 as the pinned library does. Metadata files are at most 1 MiB, at most eight
   layers and at most 256 MiB summed layer bytes. No links/special files are accepted.
5. Require empty content/snapshot ingest directories, the descriptor-addressed
   `snapshots/c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade/snapshot`
   and `snapshot-info`, matching block/ext4 root metadata and an in-root source.
   Check EXT4 magic and block geometry (at least 512 MiB and within the snapshot
   file), cap the file at 640 MiB, hash its full logical bytes and record its
   allocated bytes and metadata. No mount, filesystem repair or VM. These are
   **structural checks plus successful fresh unpack, not full fsck, an independent
   file-by-file reconstruction, guest boot proof or isolation qualification**.
6. Revalidate the same service/plist/process identities after provisioning.
   Only all checks succeeding permits `SERVICES_STARTED_INIT_CONTENT_SNAPSHOT_CHECKED`.
   Success leaves those owned services running, with no authority for a next stage.

## Approved effects and limits if this request is accepted

Downloads are restricted to the exact init OCI manifest/config/layers above and
the importer's locally generated index. Registry graph sizes are currently unknown;
the byte limits are admission checks after trusted CLI capture/retrieval, not a
claim that those bytes have already been fetched. No parent-index/tag substitution,
worker image, kernel archive, package, builder, Rosetta or other artifact.

Allow host DNS/TLS/HTTPS to **ghcr.io**, its public repository authentication
challenge/token endpoint and blob/CDN redirects solely for that immutable init
graph. HTTPS only; no manual registry login, supplied/extracted credentials or
answered login/admin/security prompt. Normal existing registry credential lookup
can occur inside the pinned image service; no credential material is collected.
No proxy/TLS configuration change or diagnostic endpoint probe is authorized.

Allow four current-manager launchd service registrations/plists, runtime/config,
image/content/ingest/snapshot writes only under `setup-v4`, normal macOS/runtime
logs/state, default host NAT and loopback DNS at `127.0.0.1:1053` and `:2053`.
Preserve default app-root/config/kernel and all old attempts. Runtime-managed
transactional temporary-file removal during normal pull/unpack is included;
Faultline itself does not delete attempt files or invoke image cleanup.

**Storage acceptance:** check 2 GiB free / 1 GiB total logical and allocated attempt
storage before startup, before pull and after pull; at most 4096 entries, depth 16,
no links/special files. The init formatter requests **minimum** 512-MiB capacity,
not an exact file length; the snapshot admission ceiling is 640 MiB. Layer admission
ceiling is 256 MiB. These are phase checks, **not live disk/download quotas**.
The CLI provides no hard service CPU/RAM/disk/network-byte limits; host services
can outlive a timed-out client. Accept that residual exposure explicitly or decline
this exact attempt; no larger storage scheme is proposed. Failure preserves bytes
and enters the scoped service recovery below, with no disk reclamation.

Zero VMs/workloads; no increase to any VM budget. One CLI at a time. Startup outer
timeout 120 s, explicit pull 180 s, status/inspect 15 s each, every observer/bootout
5 s. Ordinary stdout/stderr retain at most 64 KiB each, launchd stdout parses at
most 4 MiB without retaining environments. Bounds are checked after trusted CLI
capture, not live stream quotas. Including the previous 689-s conservative recovery
allowance, explicit pull and final ownership/process rechecks, the summed waits/
pauses ceiling is **919 s**, excluding bounded local filesystem/hash work and
scheduling. Hash reads cover up to 256 MiB of layers, 640 MiB snapshot and at most
three 1-MiB metadata blobs; no decompression/guest execution by the verifier.

## Scoped failure recovery — included only for this fresh attempt

Reuse setup-v3's tested observer and recovery implementation; never call the consumed
recovery-02 entrypoint. On startup, explicit pull, timeout or verification failure,
record failure and freeze/fsync owned service/plist/PID/UID/executable/birth identities
before removal. Recheck remaining namespaces/identities/processes before each of
at most four exact bootouts, API then machine then images then default network:

```text
/bin/launchctl bootout user/501/com.apple.container.apiserver
/bin/launchctl bootout user/501/com.apple.container.machine-apiserver
/bin/launchctl bootout user/501/com.apple.container.container-core-images
/bin/launchctl bootout user/501/com.apple.container.container-network-vmnet.default
```

Only when the observed manager is Aqua may the same exact labels be used under
`gui/501`; Background uses `user/501`. Never switch bootstrap context or run this
as an unguarded shell sequence. No prefix-wide stop, wildcard, PID kill,
cross-domain removal, retry, deletion or cache pruning. Unknown/changed/foreign
identities, failed/timed-out bootout or incomplete observations stop mutation.
Record attempted versus confirmed removals and best-effort read-only observations.
Final checks require empty scoped system/user/GUI services/Mach endpoints and old/
new relevant processes, plus unchanged prior DNS-listener baseline. At most 32 PIDs,
five final postchecks and four 1-second pauses.

The absence checks support only `SCOPED_RECOVERY_OBSERVED`; they do not prove full
vmnet teardown or arbitrary renamed-descendant absence. Interference or coordinator
death can leave services/downloads running and a partial receipt; there is no atomic
launchd compare-and-bootout. Preserve everything and obtain separate scoped recovery
approval if `INCOMPLETE_STOP_AND_REVIEW`. No old recovery authority transfers.

Validation: 49 scoped tests pass, with all service/VM calls mocked. They cover
explicit pull ordering after service checks, exit/timeout/partial-output preservation,
owned-only recovery, configured-init `[]`, corrupt/missing/linked/wrong-sized blobs,
wrong pin/platform, incomplete ingest, snapshot metadata/geometry and storage guards.
Frozen fixtures and historical receipts remain unchanged. The full suite is not
run because it includes an executing native lifetime probe. No live setup-v4 or
artifact retrieval was performed.
