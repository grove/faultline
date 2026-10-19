# Stage 1b setup-v3 — one fresh attempt requires approval

Recovery-02 is corroborated by the operator's separate [read-only process checks](2026-10-19-apple-container-recovery-02-operator-process-check.json):
the four frozen PIDs and UID-501 Container-named processes returned no matches
(exit 1, no output). These observations are operator-supplied and independent of
the recovery helper; they were not witnessed or repeated in Codex. Original
journals/receipts remain unchanged. Recovery-02 must not be repeated.

**Setup-v3 is prepared, NOT RUN and NOT AUTHORIZED.** PR #17 stays draft, issue #2
stays open, the skill stays advice-only and execution stays **NO_GO / UNAVAILABLE**.

## Exact next approval

Approve one startup attempt **including intrinsic pinned-init retrieval, host
NAT/DNS effects and the bounded ownership-verified failure recovery below**.
Working directory `/Users/grove/projects/faultline`, in operator Terminal:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B qualification/apple_container_service_setup.py setup-v3
```

Required file SHA-256 identities:

- `apple_container_service_setup.py`: `465c1d999a5bf0566f0994834d04b18bb2a96b41ebb6d48a2e940eb829e9f1ec`.
- `apple_container_recover_setup_v2.py`: `c86e1c77332d4d9bb8785c5136dedbf1d258a2aba0623a2d9d38e78c9317b6a0`.
- `apple-container-service.toml`: `ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e`.

The unchanged recovery module supplies only its tested process/listener observer
functions; its consumed recovery-02 entrypoint is **never called**. The shared setup
helper now accepts only `setup-v3`. Prior helper bytes remain at
[commit 3022586](https://github.com/grove/faultline/blob/3022586958ff88d947b5232346955440700bc149/qualification/apple_container_service_setup.py),
SHA `d9cccf3fe3cd3156525b292596e254698be1650ed1281c31b80480742f6ef837`.
Historical recovery code/plan/journal identities are retained; their consumed
command is not a recovery mechanism for setup-v3. See the [review manifest](2026-10-19-apple-container-setup-v3-review.json)
for the complete binary/config identities and machine-readable effects.

The fresh identities, created only during the approved attempt, are:

- Private directory: `/private/tmp/faultline-apple-positive-v2/setup-v3` (mode 0700).
- Source config: `setup-v3/config-home/container/config.toml` under that bundle.
- Runtime root: `/private/tmp/faultline-apple-positive-v2/setup-v3/runtime`.
- New receipt: `/private/tmp/faultline-apple-positive-v2/evidence/setup-v3.json`.

An existing receipt or directory stops the attempt; never remove either to retry.
No old runtime, image cache, receipt or default config/kernel is overwritten/pruned.
The new receipt is exclusively created, records all three source hashes, commands,
environment, observations, identities and recovery results, and is fsynced before
startup and each recovery bootout. Checkpoints update only this attempt's new file;
a coordinator failure during a write can leave a partial receipt and live services.
Preserve the file/root and obtain a fresh scoped review in that event.

## Pinned software and startup effects

Container **1.5.0**, source `d265d669ecae041bf338cb3b39c4118316d138f0`, with locked
Containerization **0.47.0 / bc994b88df46207fad7775b0eabc51947e315881**. The helper
checks the previously reviewed installed CLI/four service executable SHA-256s and
five shipped plugin config hashes before service contact. Custom or changed plugin
metadata/binaries stop it. This is an attempt identity guard; completed signature,
hardware and Stage 1a checks are not repeated.

The unchanged TOML pins init to
`ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade`
(0.47.0, arm64/v8). It also retains Kata **3.32.0** archive
`https://github.com/kata-containers/kata-containers/releases/download/3.32.0/kata-static-3.32.0-arm64.tar.zst`,
SHA `8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5`, member
`opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug`. **Kernel installation is disabled**;
no kernel archive or worker image download is requested.

The only startup subprocess is:

```text
/usr/local/bin/container system start --app-root /private/tmp/faultline-apple-positive-v2/setup-v3/runtime --install-root /usr/local --disable-kernel-install --timeout 15
```

Every child has cwd `/`, closed stdin/unrelated descriptors, and exactly:

```text
HOME=/Users/grove
PATH=/usr/bin:/bin
LC_ALL=C
TZ=Europe/Oslo
XDG_CONFIG_HOME=/private/tmp/faultline-apple-positive-v2/setup-v3/config-home
CONTAINER_APP_ROOT=/private/tmp/faultline-apple-positive-v2/setup-v3/runtime
CONTAINER_INSTALL_ROOT=/usr/local
```

The pinned [startup source](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStart.swift)
can retrieve init even with kernel installation disabled, and can log pull failure
without returning startup failure. Therefore this approval must include host
DNS/TLS/HTTPS to **ghcr.io and its blob/CDN redirects**, for this immutable init
reference and its referenced OCI content only. Expect init retrieval/unpacking for
the fresh runtime; no cache availability or payload verification is claimed.
Runtime image/content/snapshot state stays under the dedicated runtime root;
private XDG config is copied to `runtime/config/config.toml`. No worker provisioning
command is issued. Metadata inspection of this exact init is required afterward;
metadata existence is not independent payload verification or qualification.

Startup registers API/machine/image/default-network helpers with plists at
`runtime/apiserver/apiserver.plist`, `runtime/plugin-state/machine-apiserver/service.plist`,
`runtime/plugin-state/container-core-images/service.plist` and
`runtime/networks/default/service.plist`. It can create the default **host NAT**
and loopback DNS bindings at **127.0.0.1:1053 and :2053**, plus normal runtime/OS
state and logs. These host effects are not guest network attachments; no VM runs.
Normal registry credential lookup may occur. Supply/extract no credentials,
answer no login/admin/security prompt and make no manual host DNS changes.
No host source/private directory is mounted into a guest, because none is created.

## Guards, observations and failure recovery

[ServiceManager](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPlugin/ServiceManager.swift)
selects `user/501` for the demonstrated Background session, or `gui/501` for Aqua.
The helper follows the current manager without changing bootstrap context; UID
must be 501. Unsupported/unreadable sessions stop. Before startup it checks both
Container services **and Mach endpoints** in system/user/GUI, plus PID-only
Container-name discovery. Any collision/ambiguity blocks both start and stop.
It records the initial DNS-listener baseline, preserving unrelated bindings.
These fresh collision guards are part of the proposed attempt, not a replay of
completed prerequisite checks or Stage 1a inventory.

Post-start status must report running, 1.5.0, the full source commit, dedicated
app root and `/usr/local` install root. Both root comparisons use absolute existing
filesystem identity, so trailing slashes are accepted without accepting foreign
roots. Copied config bytes and nonempty exact-init metadata must match; all four
known services/Mach endpoints must be present. Only filtered launchd identities
are retained. The proven targeted observer records PID, UID, executable identity
and birth time; no whole-system ps table, arguments or environment dump is collected.
Success leaves owned services running for a separately authorized next stage.

On any startup/postcheck failure, snapshot all eligible service/plist/process
identities and fsync the recovery plan **before removal**. Verify actual nonsymlink
plist origin under setup-v3, exact label/domain, normalized effective roots,
frozen plist hash, pinned executable bytes and captured PID/UID/birth identities.
Unknown ownership, new services/endpoints or incomplete observations stop removal.
Immediately before each bootout, recheck the remaining namespace, live identities
and targeted processes. Recovery order is API, machine, images, default network,
for owned services only. For Background, the exact command candidates are:

```text
/bin/launchctl bootout user/501/com.apple.container.apiserver
/bin/launchctl bootout user/501/com.apple.container.machine-apiserver
/bin/launchctl bootout user/501/com.apple.container.container-core-images
/bin/launchctl bootout user/501/com.apple.container.container-network-vmnet.default
```

Aqua uses the same four exact labels under `gui/501`, only when that is the recorded
current-manager domain. Never run these as a bare shell sequence. No global stop,
wildcard, cross-domain removal, process kill or file deletion is authorized.
Afterward check all three registration/Mach namespaces, old/new relevant processes
and reviewed DNS bindings. Only no scoped processes/registrations plus the unchanged
prior listener baseline permits `SCOPED_RECOVERY_OBSERVED`. A failed/timed-out
bootout or lingering/replaced process stops further mutation, preserves attempted
versus confirmed removals, and records best-effort read-only partial observations.
`INCOMPLETE_STOP_AND_REVIEW` means no retry, forced cleanup, provisioning or execution;
a new recovery requires fresh identities and separate approval.

Keep all other Container management idle. Launchd has no atomic identity comparison
and removal; interruption or interference can leave partial state. These checks do
not prove complete vmnet teardown or detect arbitrary renamed descendants. No
sandbox restriction is relaxed or bypassed. A setup success is not a smoke test or
execution-safety qualification.

Budgets: **zero VMs/workloads**, no change to the proposed 2-vCPU / 512-MiB VM ceiling.
One client at a time; startup outer timeout **120 s**, CLI API-readiness timeout
**15 s**, status/init inspection **15 s each**, every observation/bootout **5 s**.
At most four removals, 32 relevant process IDs, five postchecks/four 1-second pauses.
A conservative sum of waits/pauses, including late failure and partial observations,
is **689 s**, excluding local hashing/filesystem/scheduling delays. At most 64 KiB
per ordinary stream and 4 MiB for launchd parsing, checked after trusted CLI capture;
these are not hard live memory/output quotas. Host services have **no hard CPU/RAM/
disk quota** supplied by this CLI and can outlive the setup client. Init's source-defined
512-MiB sparse snapshot capacity is not an aggregate host-storage quota or VM allocation.
Accept these setup-only host effects explicitly; do not silently transfer a VM budget.

Validation: **43 scoped tests passed**, including Aqua/Background, actual macOS
process rows, normalized status/network paths, startup exit/timeout, missing init
metadata, collisions, foreign/changed identities, replaced/lingering processes,
partial cleanup, normal startup stderr and consumed receipt reuse. All service/VM
commands are mocked. No setup-v3, artifact retrieval, VM/canary or #10 has run.
