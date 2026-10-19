# Guardian installation and host-fixture lifetime calibration v1

**PREPARED; NOT INSTALLED OR RUN. Separate operator authorization required.**
Provision-v3 is **CONSUMED SUCCESS; DO NOT REPEAT**. Its unchanged original receipt
SHA-256 is `e082359d42a2d24690c10cd16d220cb55783d2f6b68c5d9210333d5a4dafdea0`,
result `WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM`. See the
[provenance-qualified outcome](2026-10-19-apple-container-provision-v3-outcome.json)
and [byte-for-byte receipt copy](2026-10-19-apple-container-provision-v3.json).
Historical procedures, reviews, receipts, fixtures, helpers and artifacts remain
unchanged. This document supersedes their *next-action* suggestions only.
PR #17 stays draft, issue #2 stays open, execution **NO_GO / UNAVAILABLE**.

## One authorization request

Authorize **one** operator-Terminal execution of the command below, from
`/Users/grove/projects/faultline`, to register and remove only four new host-fixture
jobs in **user/501**, in two sequential attempts. It deliberately interrupts each
coordinator and the second guardian. It records whether launchd restarts the latter
and whether the original deadline stops the exact fixture. This is neither a VM
installation nor a VM lifetime/descendant qualification. Approval is required by
the user's explicit boundary between preparing this stage and installing it.

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B -c '
import hashlib
from pathlib import Path
path = Path("/Users/grove/projects/faultline/qualification/apple_container_guardian_calibration_v1.py")
source = path.read_bytes()
if hashlib.sha256(source).hexdigest() != "89c5e3a23bef60672b6818dcb8ed421ffc3907b70f5e5cd76908bd6dbe309013":
    raise SystemExit("guardian-calibration-v1 source hash mismatch")
exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})
' install-calibrate-v1
```

The wrapper executes exactly the bytes it hashes. Source and regression hashes:

| File | SHA-256 |
| --- | --- |
| `qualification/apple_container_guardian_calibration_v1.py` | `89c5e3a23bef60672b6818dcb8ed421ffc3907b70f5e5cd76908bd6dbe309013` |
| `tests/test_apple_container_guardian_calibration_v1.py` | `095880134769a95a65f69491f3b7ba8eeaee69e07ea2a75a9dd0882d46a1886a` |

The helper imports only standard-library modules. It pins both existing host Python
launcher and framework executable (no installation or upgrade):

| Host path | SHA-256 |
| --- | --- |
| `/opt/homebrew/Cellar/python@3.15/3.15.0/Frameworks/Python.framework/Versions/3.15/bin/python3.15` | `1955899cb535256cfa477d926d016819e52e747984722c44f76e39a4950fee0e` |
| `/opt/homebrew/Cellar/python@3.15/3.15.0/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python` | `409ddb09021ac53577e7658de9ec09c899655c77a38744679ef73be9af21ecd5` |

## Exact registration, commands and effects

Require UID 501 and launchctl manager `Background`. Refuse the existing stage root
or any of the four labels before creating state. No rerun over a consumed identity.
Let `B=/private/tmp/faultline-guardian-calibration-v1`, and let `C` be, in order,
`coordinator-loss` then `guardian-restart`. Each directory is `B/C`, mode **0700**.
For each `C`, the only labels are:

```text
dev.faultline.guardian-calibration-v1.C.guardian
dev.faultline.guardian-calibration-v1.C.fixture
```

Here `C` denotes literal substitution of those two named cases; these are the four
exact permitted targets under `user/501/`. Plist files use their full label plus
`.plist` under `B/C`; each is **0400**. No file goes into `~/Library/LaunchAgents`,
`/Library/LaunchDaemons`, the existing Container runtime, or the worker filesystem.
Registration persists in the current user launchd domain until bootout/logout;
there is no login/reboot auto-install, enable/disable or system-domain change.

Each job's exact `ProgramArguments` are the resolved pinned Python launcher,
`-I`, `-B`, the absolute new helper path, its role (`guardian` or `fixture`), and
`B/C/plan.json`. `WorkingDirectory=/`; environment is exactly `PATH=/usr/bin:/bin`,
`LC_ALL=C`, `TZ=Europe/Oslo`; stdin is closed for coordinator/CLI subprocesses.
Both plists have `RunAtLoad=true`, `ProcessType=Background`, `ExitTimeOut=1`.
Only guardian has `KeepAlive={SuccessfulExit:false}`, `ThrottleInterval=1`.
See the installed `launchd.plist(5)` manual and
[Apple's launchd manual source](https://github.com/apple-oss-distributions/launchd/blob/main/man/launchd.plist.5).
The one-second throttle is a request, not an observed restart-latency guarantee.

The complete subprocess command family is:

```text
/bin/launchctl managername
/bin/launchctl print user/501
/usr/sbin/sysctl -n kern.boottime
/bin/ps -ww -p PID -o pid=,uid=,lstart=,comm=
/bin/launchctl print user/501/LABEL
/bin/launchctl bootstrap user/501 B/C/LABEL.plist
/bin/launchctl bootout user/501/LABEL
/bin/launchctl kill SIGKILL user/501/LABEL
PINNED_PYTHON -I -B ABSOLUTE_HELPER coordinator B/C/plan.json
```

`LABEL` is restricted to the four labels above. `PID` is only the installer itself,
its own coordinator, or the guardian/fixture PID bound from the exact registration.
The installer uses its retained `Popen.kill()` handle to SIGKILL only its own
coordinator, after rechecking PID/UID/executable/birth. In the second case only, it
identity-checks the guardian registration twice, journals intent and invokes its
exact-target SIGKILL. It does not kill the fixture itself: the launchd-supervised
guardian owns that action. Launchd invokes the two plist commands; fixtures run only
trusted host helper code (`alarm(30); sleep(30)`) and create no descendants. The
fixture alarm is an additional cooperative failsafe, never the passing oracle.

These actions contact local launchd and can produce ordinary macOS logs. No
Container/XPC service contact, network, artifact retrieval, provisioning, VM
configuration creation/bootstrap, canary, target-project execution, #10, Faultline
skill enablement, global shutdown, process-name kill, or unrelated file mutation.
The existing four Container services are outside all effect targets.

## Deadline, ownership, recovery and cleanup

Before guardian bootstrap, fsync **0400** `plan.json`, both plists and their parent.
The plan seals the case, source/interpreter/plist hashes, exact directory/labels,
`kern.boottime`, `armed_monotonic`, and `deadline_monotonic=armed_monotonic+10`.
The original absolute deadline is never rearmed, renewed by heartbeat, or changed
on restart. Reboot/clock reset, invalid/nonfinite interval or changed source/plan
scope prevents automatic action. A **0400** `ready.json` binds the plan hash.
The coordinator requires that readiness, the exact live guardian, fixture absence,
and at least five seconds of the original budget before fixture bootstrap.

The guardian owns **0600** append-only `guardian.jsonl` in the host-only case root.
Each ARMED/STARTED/OWNED/action-intent/terminal record and parent directory are
fsynced. OWNED captures target, plist origin/hash, PID, UID, executable and `lstart`
birth. Live registration must match the exact origin, program and full argv;
source and both executable hashes are rechecked. Parent paths cannot be symlinks;
plan/plist/journal ownership, modes, single-link and one-MiB bounds are checked.
A registered job without a process during fixture observation is inconclusive,
not absence; the attempt may safely fail during an unexpected launchd transition.

At the original deadline, revalidate registration and independent targeted `ps`
identity, persist `BOOTOUT_INTENT`, then bootout only the exact fixture target.
If stop is not independently observed, revalidate again before the sole SIGKILL
fallback. A successful fixture stop requires **both** registration absence from a
successful domain inventory and independent captured-PID absence. Guest text,
fixture alarm, CLI exit and missing status metadata are insufficient. PID birth
has `ps lstart` precision; checks plus action are not atomic. This trusted-fixture
calibration does not qualify hostile same-UID replacement or VM descendants.

Coordinator death leaves the guardian supervised by launchd. Guardian abnormal
death invokes launchd's restart policy; replay restores the original owner and
deadline. An intent without completion may be retried only after exact identity
revalidation, against the same target and deadline. Terminal records are inert.
A torn/malformed journal, foreign/reused identity, unregistered live PID, changed
origin/source/boot, or inaccessible observation causes **INCOMPLETE_STOP_AND_REVIEW**:
no uncertain target is killed, no second case is started, and no retry/repair is
attempted. Handled errors exit successfully to avoid an automatic restart loop.
Abrupt death can leave partial state; preserve it for separately scoped recovery.

After fixture stop, the installer independently repeats registration/PID checks,
waits for the guardian's own PID(s) to disappear, validates its retained stopped
registration, and bootouts only that exact guardian label. It checks registration
absence again. **No evidence, metadata directory, plist or old artifact is deleted.**
If installer interruption leaves a stopped guardian registered, later recovery
requires reviewing the sealed plan/journals and the same identity/absence checks;
this authorization does not grant a later manual retry or wider cleanup.

Every CLI/ps/sysctl subprocess has a one-second timeout. Polls are 50 ms; after
each termination action, at most five 100-ms postcheck intervals are attempted.
Readiness budget is three seconds, ownership must be observed by deadline minus
three, and final installer observation stops at armed time plus **25 seconds** per
case (up to 50 seconds for both, plus bounded in-flight observations/preflight).
Filesystem/hash/scheduling waits and launchd recovery are not hard real-time
bounds. The deadline triggers a stop attempt; this is explicitly **not a guaranteed
ten-second lifetime cutoff**. Any missed budget is incomplete, never a pass.

## Evidence and present validation

All new live evidence remains under `B`: `attempt.json`, then each case's
`plan.json`, two plists, `ready.json`, `guardian.jsonl`, `operator.jsonl` and
`result.json`; finally root `result.json`, or exclusive root `failure.json` on a
handled post-creation failure. Preserve all partial files on interruption. A
preflight refusal before root creation writes no new receipt. Live result may
claim only `CALIBRATED_HOST_FIXTURES_ONLY`, with VM containment **UNQUALIFIED**.

**74 scoped tests passed**, including six new tests: real host coordinator and
guardian subprocess interruption/restart with **synthetic identity/registration
observations and a cooperative host fixture**, fixed-deadline replay, crash after
action intent, replaced/unregistered owner rejection, torn journals/invalid clocks,
exact plist/argv/origin checks and timeout fallback. No test registers launchd.
Attempting independent `/bin/ps` in this restricted session returned
`PermissionError: Operation not permitted`; that process-observation test is
**UNAVAILABLE here**, not passing containment evidence. The cooperative fixture
exits on a host marker removed by the tested watchdog; this validates recovery
control flow, not forced termination or live launchd restart semantics.

## Separate future VM identity gate — NOT AUTHORIZED

Successful installation or either host-fixture result does **not** prove that a
VM or its detached/Virtualization.framework descendants are contained. Before any
separate VM request, freeze a reviewed coordinator/guardian revision, fresh
container configuration and creation identity. The previously prepared mapping is:

- ID/UUID: `faultline-apple-positive-v3`; root:
  `/private/tmp/faultline-apple-positive-v2/setup-v4/runtime/containers/faultline-apple-positive-v3`.
- Exact target:
  `user/501/com.apple.container.container-runtime-linux.faultline-apple-positive-v3`.
- Origin: that root's `service.plist`; arguments:
  `/usr/local/libexec/container/plugins/container-runtime-linux/bin/container-runtime-linux start --root ROOT --uuid faultline-apple-positive-v3`.
- Runtime binary SHA-256:
  `e8bee184cc1f6b53982f9cc4ecb02085ebe238b8834112f71f8972c0d488511a`;
  app root is the existing `setup-v4/runtime`, install root `/usr/local`.
- Dedicated kernel is provision-v3's unchanged **0444**, 30,423,552-byte file,
  SHA-256 `fb2cfb79eb1ae19447a85d75682d7fa5cfec97e24beb2609a492b806e8072c8d`.

Before start, require absent target/root, immutable config/source/artifact locks,
an independently supervised guardian ready against a sealed original deadline,
and explicit approval of the entire stop/observation window. Bind actual live
registration, complete arguments/root/UUID, executable bytes, PID/UID/birth to the
created object before any termination. Foreign or uncertain identities are left
untouched. Prove runtime registration and captured VM-owner PID absence separately;
then independently account for auxiliary VM processes, detached descendants and
vmnet teardown. Those observations and adversarial/resource/network controls
remain missing. The historical guardian helper is preserved, not declared VM-ready
by these new tests. No VM coordinator, create/start command or metadata deletion
is included in this request.
