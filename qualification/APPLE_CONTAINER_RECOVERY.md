# Setup-v2 recovery-01 — consumed attempt, no removal

**This command is historical and must not be rerun.** Recovery-01 stopped at process
parsing with `attempted: []`, `removed: []`. Its journal is preserved. The only
current request is [recovery-02](APPLE_CONTAINER_RECOVERY_02.md), requiring fresh
approval and a new journal. Old recovery source/hashes remain in Git at `c82a52f`.
The remaining text records the consumed recovery-01 proposal.

PR #17 stays draft, issue #2 stays open, and execution is **NO_GO / UNAVAILABLE**.
No cleanup has run. Do not repeat setup-v2, start services or provision artifacts.

## Result and provenance

The original `/private/tmp/faultline-apple-positive-v2/evidence/setup-v2.json`
is unchanged, SHA-256
`9cca8060f4314ef1ba6ef1fe430dc2318d81f8f2de3501d90a205e5f8c466ce4`;
its [raw copy](2026-10-18-apple-container-setup-v2.json) preserves the failed result.
The operator reports exit 1: startup exited 0 and status reported running, but
Faultline rejected trailing-slash roots. Its attempted recovery rejected the
network helper before any bootout. No VM/canary ran. The setup authorization is
consumed; the failure does not authorize another startup or recovery attempt.

The receipt's script SHA `8c01df30a82fc4f5b5c1d6eb734e61f5a9ca31932acbc854de203c0e8c4098a7`
independently matches [the reviewed setup-v2 source](https://github.com/grove/faultline/blob/2486ec3f8a2b2a11225b37fdf4a7d490934e9d1e/qualification/apple_container_service_setup.py).
The unchanged TOML SHA is
`ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e`.
Receipt/file/source comparisons are independently verified; the original command's
execution remains operator-supplied evidence. Historical sources remain in Git;
all previous receipts and frozen fixture identities are preserved.

Apple Container 1.5.0's pinned
[PluginLoader](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPlugin/PluginLoader.swift)
sets plugin roots using directory URL paths, accounting for trailing slashes.
[ServiceManager](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPlugin/ServiceManager.swift)
maps Background to `user/<uid>` for registration/removal. Both app and install
roots now require absolute, existing paths with equal filesystem identity
(`Path.samefile`), allowing directory slash differences. Missing/foreign paths
fail closed. Label, domain, actual live plist origin, executable and plist hash
checks remain mandatory. A prefix match alone never establishes ownership.

## Independently observed identities

Read-only launchd/plist inspection corroborated the operator's API/network
observations and obtained the remaining machine/image identities. All four were
running in **user/501**, with actual plist origins under
`/private/tmp/faultline-apple-positive-v2/setup-v2/runtime` (abbreviated `R` below).
The [frozen plan](2026-10-18-apple-container-recovery-plan.json) records every
absolute path, argv, plist SHA, executable SHA, effective roots and Mach name.

| Exact launchd label | PID | Actual plist origin relative to R | Executable |
| --- | --- | --- | --- |
| `com.apple.container.apiserver` | 70913 | `apiserver/apiserver.plist` | `/usr/local/bin/container-apiserver` |
| `com.apple.container.machine-apiserver` | 70924 | `plugin-state/machine-apiserver/service.plist` | `/usr/local/libexec/container/plugins/machine-apiserver/bin/machine-apiserver` |
| `com.apple.container.container-core-images` | 70925 | `plugin-state/container-core-images/service.plist` | `/usr/local/libexec/container/plugins/container-core-images/bin/container-core-images` |
| `com.apple.container.container-network-vmnet.default` | 70921 | `networks/default/service.plist` | `/usr/local/libexec/container/plugins/container-network-vmnet/bin/container-network-vmnet` |

All effective app roots identify R; all install roots identify `/usr/local`.
API paths lack trailing slashes; the other three include them. Plist labels,
programs, arguments and environment agree with the dedicated setup-v2 root.
No other Container services/endpoints were observed in system/user/GUI inventories.
Read-only lsof observed API PID 70913 UDP `127.0.0.1:2053`; no 1053 binding appeared.
This is not evidence of successful NAT/DNS initialization or full containment.

Codex denied `/bin/ps` under its existing restrictions. No escalation or alternate
bypass was attempted. The proposed operator-Terminal recovery requires successful
process observation **before any bootout**; it cannot claim process ownership or
cleanup success from registration absence alone.

## Historical recovery-01 authorization — consumed

Approve **one recovery-only execution**, from `/Users/grove/projects/faultline`,
in the operator's normal Terminal, keeping all other Container management idle:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C /opt/homebrew/bin/python3 -I -B qualification/apple_container_recover_setup_v2.py recover-setup-v2-01
```

Reviewed SHA-256 identities:

- Recovery helper: `63207c550a9b5f9391e4b7cf28f5d4305a36ae5a7b1da9a0db2159a72318bcf3`.
- Shared identity helper: `d9cccf3fe3cd3156525b292596e254698be1650ed1281c31b80480742f6ef837`.
- Frozen plan: `f727a96cbea4ac6751aa00894049c35b5c1b0d5a8206e36757f96734f643f9a9`.

The helper verifies the plan, shared helper and original receipt hashes, requires
UID 501, and exclusively creates this new append-only, fsynced journal:

`/private/tmp/faultline-apple-positive-v2/evidence/recovery-setup-v2-01.jsonl`

An existing journal blocks reuse. Do not delete it to retry. No other file write
is requested; launchd/service shutdown may update normal runtime/OS logs/state.
The helper uses cwd `/`, closed stdin, no inherited credentials/environment, and
only `PATH=/usr/bin:/bin`, `LC_ALL=C` for child commands. It reads the frozen plan,
receipt, exact plists/executables, launchd tables, process metadata and socket
metadata. It requests no network access, download, VM/workload allocation or new
service. It supplies no sudo/admin/Keychain credentials or sandbox relaxation.

Before the first mutation, it validates all four live targets/origins/hashes,
programs/effective roots, PIDs, executable bytes, process UID/path and birth time,
all three registration namespaces, and the listener baseline. It repeats target,
process and namespace checks immediately before each removal, journaling first.
The **only mutating subprocesses**, in this order, are:

```text
/bin/launchctl bootout user/501/com.apple.container.apiserver
/bin/launchctl bootout user/501/com.apple.container.machine-apiserver
/bin/launchctl bootout user/501/com.apple.container.container-core-images
/bin/launchctl bootout user/501/com.apple.container.container-network-vmnet.default
```

These are the guarded helper's effects, not an unguarded shell sequence to run.
No global `container system stop`, wildcard, process kill, cross-domain bootout,
file deletion, restart, image command, container, canary or experiment #10 runs.

After removal it checks `launchctl print system`, `user/501`, `gui/501` for
Container services **and Mach endpoints**; `/bin/ps -ww -axo pid=,uid=,lstart=,comm=`
for the frozen PIDs or same-user expected executable names; and
`/usr/sbin/lsof -nP -i:1053,2053 -F pPn` for the reviewed DNS bindings. Unrelated
existing listeners must remain unchanged; they are never stopped. Process metadata
retains only scoped records, no command arguments/environment. Raw launchd output
is discarded. Only absence of scoped registrations/processes and owned bindings
with unchanged foreign bindings permits `SCOPED_RECOVERY_OBSERVED`.

Each subprocess has a 5-second timeout; at most five postchecks with four 1-second
pauses. Maximum summed waits including late failure observation: 319 seconds,
excluding local hashing/filesystem/scheduling delays. Trusted CLI capture is
checked at 4 MiB after capture; it is not a hard live memory/output quota. No new
VM/process resource budget is granted; this stops existing services only.

Any stale PID, changed executable/plist/root, foreign/new service/endpoint,
unreadable/ambiguous observation, timeout, failed bootout or residual state stops
mutation. After an attempted bootout, best-effort read-only partial observations
are recorded; no further cleanup is attempted on failure. A timed-out bootout may
already have taken effect. Preserve the journal and request a fresh, identity-scoped
review/approval; never rerun this identity or proceed to startup/provisioning.

Launchd has no atomic compare-and-bootout operation. Exclusive Container management
is required; interference or coordinator death can leave partial state. This plan
does not prove vmnet teardown, detect arbitrary renamed descendants, or qualify a
sandbox. A successful recovery only resolves the scoped service state; synthetic
execution and negative controls remain separately authorized future stages.

Validation: 30 mocked Apple Container tests cover Aqua/Background, slash-normalized
status/network roots, foreign origin/executable/hash, collision rejection, startup
failure, complete/partial/ambiguous cleanup, denied process observation and lingering
processes. No live recovery or VM test has been run.
