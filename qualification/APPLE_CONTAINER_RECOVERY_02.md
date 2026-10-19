# Recovery setup-v2-02 — separate one-attempt approval required

PR #17 remains draft, issue #2 remains open, and execution is **NO_GO / UNAVAILABLE**.
No cleanup, restart, artifact provisioning, VM, canary or #10 is authorized here.

## Preserved failure and diagnosis

The original `evidence/recovery-setup-v2-01.jsonl` is unchanged; its
[byte-identical copy](2026-10-19-apple-container-recovery-01.jsonl) has SHA-256
`72b99a00ad4bdd2005777b364530e2d5c2ee217fadd20d1fa3b4e0c3703dd770`.
It records `ValueError: Unrecognized process observation`, `attempted: []` and
`removed: []`. The failed attempt consumed recovery-01's authority. The original
setup-v2 receipt remains SHA-256
`9cca8060f4314ef1ba6ef1fe430dc2318d81f8f2de3501d90a205e5f8c466ce4`;
all earlier receipts, frozen fixtures and source identities remain preserved.
The old recovery source is retained at
[commit c82a52f](https://github.com/grove/faultline/blob/c82a52f1286331f3ea46a1f1c272223080a301f5/qualification/apple_container_recover_setup_v2.py),
SHA-256 `63207c550a9b5f9391e4b7cf28f5d4305a36ae5a7b1da9a0db2159a72318bcf3`.

That source ran whole-system `ps -ww -axo pid=,uid=,lstart=,comm=` and required
eight fields on **every row before filtering for relevant PIDs/names**. Its generic
error retained no rejected row. The four later operator-supplied rows satisfy
that guard, but cannot identify the earlier offending row or missing field.
It is unknown whether the rejected row was unrelated or a transient relevant
observation. No unrelated row is blamed, collected or published to investigate.
The defect being corrected is the dependency on unscoped process-table formatting.

The actual [targeted rows](2026-10-19-apple-container-operator-processes.txt) are an
operator-supplied fixture, not independently collected process evidence. All are
UID 501 with the expected executable paths. Their birth strings are pinned using
the declared host timezone, `Europe/Oslo`:

| PID | Service | Birth time, 2026-10-18 |
| --- | --- | --- |
| 70913 | API | 23:31:23 |
| 70921 | network | 23:31:24 |
| 70924 | machine | 23:31:25 |
| 70925 | images | 23:31:26 |

Independent read-only launchd checks on 2026-10-19 again found those four running
services in `user/501`; actual plist origins, effective roots, plist hashes and
executable hashes still match setup-v2. System/user/GUI registration and Mach
endpoint allowlists match. Full identities and birth strings are in the
[new frozen plan](2026-10-19-apple-container-recovery-02-plan.json). No process
inspection was rerun in Codex or restriction bypass attempted.

## Process observation and stopping rules

The collector first receives **only relevant PIDs** from:

```text
/usr/bin/pgrep -u 501 ^(container-|machine-api)
```

The pattern is one argv item, with no shell. Native process-name filtering uses
broad prefixes so truncated names and additional Container-named helpers remain
candidates. It uses no `-f`/argument output. The installed
`/usr/share/man/man1/pgrep.1` documents name matching, effective UID filtering and
exit 1 for no match; Apple's [pgrep source](https://github.com/apple-oss-distributions/adv_cmds/blob/main/pkill/pkill.c)
also shows a shortened-name fallback. This is source/manual review, not independent
calibration of the installed selector. Before removal, the selector must account
for **all four live expected processes**, or the attempt stops untouched.

One targeted query covers the union of discovered candidates and the four frozen
PIDs, sorted, with at most 32 PIDs total. Initially its exact argv is:

```text
/bin/ps -ww -p 70913,70921,70924,70925 -o pid=,uid=,lstart=,comm=
```

No `-a`/`-A`/`-x` system-wide selection is used. A second PID-only discovery must
match the first; every discovered PID must have an unambiguous targeted row.
PID, UID, absolute executable filesystem identity and birth time must match the
frozen plan for **every remaining service** before each bootout. Relevant malformed,
duplicate, missing, extra, replaced or stale processes block mutation. No row is
silently discarded. After removals, original PIDs are still queried, and new or
lingering Container-named processes prevent a cleanup-success result. They are
observed, never killed. A replacement of a frozen PID is likewise not absence.

Native tools necessarily inspect the host process catalog internally; Python
receives no unfiltered process table, argument lists or environments. Only scoped
PID identity records enter the journal. Unknown relevant formats fail with an
error with only a scoped row number/field count or PID, without dumping the row. Exit 1 with empty stdout/stderr is accepted as no
match only for the fixed discovery, targeted ps and lsof observations; permission
diagnostics, other statuses and ambiguous success-with-empty-output stop recovery.
The [Apple ps source](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/ps.c)
returns 1 when no selected entries remain. This does not reinterpret permission
failures as absence or authorize relaxing Codex restrictions.

## Exact separate authorization request

Approve **one recovery-setup-v2-02 attempt**, in operator Terminal, with all other
Container management idle. Working directory: `/Users/grove/projects/faultline`.

```sh
/usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B qualification/apple_container_recover_setup_v2.py recover-setup-v2-02
```

Required file SHA-256 identities:

- `apple_container_recover_setup_v2.py`: `c86e1c77332d4d9bb8785c5136dedbf1d258a2aba0623a2d9d38e78c9317b6a0`.
- `apple_container_service_setup.py`: `d9cccf3fe3cd3156525b292596e254698be1650ed1281c31b80480742f6ef837`.
- `2026-10-19-apple-container-recovery-02-plan.json`: `26b72f4f05406f714c2f6ac92fdaba9d5fe39b6b387bb4f4568c43274146e679`.
- Operator fixture (test input): `5f0c34272328d4a787c460047669848925bbae110053cb6ea491227714e69f1c`.

The helper verifies the plan, shared identity helper, original setup-v2 receipt
and previous recovery journal hashes, requires UID 501, and exclusively creates:

`/private/tmp/faultline-apple-positive-v2/evidence/recovery-setup-v2-02.jsonl`

It never overwrites/reuses recovery-01. Existing recovery-02 evidence blocks a
repeat; preserve it and obtain a fresh review/identity instead. Every child uses
cwd `/`, closed stdin, and only `PATH=/usr/bin:/bin`, `LC_ALL=C`, `TZ=Europe/Oslo`.
It reads the reviewed files, exact installed plists/executables and scoped OS
observations. Only the new fsynced journal is written directly. Normal service/OS
shutdown state and logs may change. No network permission, credential, sudo,
service startup, filesystem deletion, artifact retrieval or VM budget is requested.

All service/plist guards are unchanged: exact domain/label, actual nonsymlink
plist origin under setup-v2, frozen plist/executable hashes, effective app/install
root identities, live executable and frozen PID. Before any mutation all four
identities and processes must pass; immediately before each bootout the remaining
namespace, target identity and process set are revalidated and journaled. The only
mutating commands remain, in this order:

```text
/bin/launchctl bootout user/501/com.apple.container.apiserver
/bin/launchctl bootout user/501/com.apple.container.machine-apiserver
/bin/launchctl bootout user/501/com.apple.container.container-core-images
/bin/launchctl bootout user/501/com.apple.container.container-network-vmnet.default
```

Run the guarded helper, not a bare bootout sequence. No prefix-wide stop,
cross-domain removal or process kill is allowed. Postchecks cover all three
registration/Mach namespaces, scoped processes and `lsof -nP -i:1053,2053 -F pPn`.
Owned bindings must disappear; unrelated existing listeners must remain unchanged.
Only then may the journal report `SCOPED_RECOVERY_OBSERVED`.

Every subprocess is bounded to 5 seconds; five postchecks/four 1-second pauses
maximum. Summed subprocess waits including late-failure observation are at most
429 seconds, excluding filesystem/scheduling delays. Output is checked after
trusted CLI capture at 4 MiB, not hard stream/memory quotas. No host service or VM
budget increase is granted. Any ambiguity, drift, failed/timeout bootout or residual
state stops further mutation, records incomplete recovery and attempts read-only
partial observations. A timeout may already have caused removal; never auto-retry.

Exclusive management remains required: launchd has no atomic identity comparison
and removal. Interruption can leave partial state. Checks do not establish complete
vmnet teardown or cover arbitrary renamed descendants. Success means scoped
service recovery, never execution-safety qualification or later startup authority.

Validation: 36 scoped tests, including the actual operator rows, missing/stale PIDs,
wrong UID/path/birth time, replacement before bootout, extra helpers, old/new lingering
PIDs, malformed relevant rows, discovery races, denial versus absence, strict plist
identity, partial cleanup and ambiguous bootout. All OS commands are mocked in tests;
no recovery or native lifetime probe was executed.
