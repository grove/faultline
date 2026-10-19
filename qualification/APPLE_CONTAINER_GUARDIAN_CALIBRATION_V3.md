# Guardian host-fixture calibration v3 — explicit Background session

**PREPARATION ONLY; V3 NOT AUTHORIZED / NOT RUN.**

Calibration-v1 and calibration-v2 are both **CONSUMED FAILURE; DO NOT REPEAT**.
All their original source, procedures, reviews, live evidence, hashes and modes
remain unchanged. Historical NOT RUN/unknown-cause records remain historical;
[this new diagnostic and preservation manifest](2026-10-19-apple-container-guardian-calibration-v2-diagnostic.json)
records the later v2 outcome and supersedes their next-action suggestions only.
Provision-v3 remains **CONSUMED SUCCESS; DO NOT REPEAT**, receipt SHA-256
`e082359d42a2d24690c10cd16d220cb55783d2f6b68c5d9210333d5a4dafdea0`.
PR #17 stays **draft**, issue #2 **open**, Faultline execution **NO_GO / UNAVAILABLE**.
Publication grants no execution permission.

The operator supplied a unified-log row at **2026-10-19 12:40:22.972**:

```text
[user/501:] Bootstrap by launchctl[94871] for <private> failed (134: Service cannot load in requested session)
```

This is an **operator-correlated** first v2 guardian bootstrap rejection, underlying
launchd error **134**, distinct from the preserved CLI exit **5** and generic I/O
stderr. The log redacts the service; the receipt does not independently bind the
CLI PID. The operator also reports no Faultline calibration override in
`launchctl print-disabled user/501`. The full log archive, query argv and raw
disabled inventory were not supplied; the timestamp's timezone was not specified.
No live log or launchd query was repeated here. V1's underlying cause remains
undetermined; this evidence identifies the v2 rejection.

Offline review confirms that both original v2 plists omit `LimitLoadToSessionType`.
[Apple TN2083, launchd Agent](https://developer.apple.com/library/archive/technotes/tn2083/_index.html)
documents the per-user Background session and an Aqua default when the session
constraint is omitted. This archived guidance was reviewed on 2026-10-19; it is
not a new live acceptance test. The pinned installed `launchd.plist(5)` separately
defines `LimitLoadToSessionType` (lines 163–166) and `ProcessType` resource
classification (584–595). Its unchanged SHA-256 is
`1c5f5041c1d3492988bfa6f9dc6d969dfd072d20af2703c28d9a8f6ed6aaadcb`.
V3 adds the explicit Background session in the shared generator for both jobs,
retains `user/501`, UID 501 and all modes/deadlines/identity checks, and strengthens
live full-plist verification. It does not claim observed launchd acceptance.

The new evidence root below is **reserved by this procedure and currently absent**.
It is created exclusively by the approved command, not by preparation. An existing
root, symlink or exact label is a stop condition, never permission to reuse it.

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
path = Path("/Users/grove/projects/faultline/qualification/apple_container_guardian_calibration_v3.py")
source = path.read_bytes()
if hashlib.sha256(source).hexdigest() != "2c431ec7b99a6424eee8b7b7fcbff1eaf1c2b28fa2503b8a804ef587827ecc02":
    raise SystemExit("guardian-calibration-v3 source hash mismatch")
exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})
' install-calibrate-v3
```

The wrapper executes exactly the bytes it hashes. Source and regression hashes:

| File | SHA-256 |
| --- | --- |
| `qualification/apple_container_guardian_calibration_v3.py` | `2c431ec7b99a6424eee8b7b7fcbff1eaf1c2b28fa2503b8a804ef587827ecc02` |
| `tests/test_apple_container_guardian_calibration_v3.py` | `d1af20886f4ce8b3b2c6901b7bf680e1f9b9e6b2e45b3a183b180cbac5bd0a01` |

The helper imports only standard-library modules. It pins both existing host Python
launcher and framework executable (no installation or upgrade):

| Host path | SHA-256 |
| --- | --- |
| `/opt/homebrew/Cellar/python@3.15/3.15.0/Frameworks/Python.framework/Versions/3.15/bin/python3.15` | `1955899cb535256cfa477d926d016819e52e747984722c44f76e39a4950fee0e` |
| `/opt/homebrew/Cellar/python@3.15/3.15.0/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python` | `409ddb09021ac53577e7658de9ec09c899655c77a38744679ef73be9af21ecd5` |

## Exact registration, commands and effects

Require UID 501 and launchctl manager `Background`. Refuse the existing stage root
or any of the four labels before creating state. No rerun over a consumed identity.
Let `B=/private/tmp/faultline-guardian-calibration-v3`, and let `C` be, in order,
`coordinator-loss` then `guardian-restart`. Each directory is `B/C`, mode **0700**. The root is also **0700**.
For each `C`, the only labels are:

```text
dev.faultline.guardian-calibration-v3.coordinator-loss.guardian
dev.faultline.guardian-calibration-v3.coordinator-loss.fixture
dev.faultline.guardian-calibration-v3.guardian-restart.guardian
dev.faultline.guardian-calibration-v3.guardian-restart.fixture
```

These are the four exact permitted targets under `user/501/`. Plist files use their full label plus
`.plist` under `B/C`; each is **0400**. No file goes into `~/Library/LaunchAgents`,
`/Library/LaunchDaemons`, the existing Container runtime, or the worker filesystem.
Registration persists in the current user launchd domain until bootout/logout;
there is no login/reboot auto-install, enable/disable or system-domain change.

Each job's exact `ProgramArguments` are the resolved pinned Python launcher,
`-I`, `-B`, the absolute new helper path, its role (`guardian` or `fixture`), and
`B/C/plan.json`. `WorkingDirectory=/`; environment is exactly `PATH=/usr/bin:/bin`,
`LC_ALL=C`, `TZ=Europe/Oslo`; stdin is closed for coordinator/CLI subprocesses.
Both plists have `RunAtLoad=true`, `ProcessType=Background`,
`LimitLoadToSessionType=Background` (a string), and `ExitTimeOut=1`.
The process type classifies resources; the session key explicitly selects the
per-user Background session. Both bootstrap and live observation compare the
complete plist against the exact generated definition, in addition to its hash.
Only guardian has `KeepAlive={SuccessfulExit:false}`, `ThrottleInterval=1`.
See the installed `launchd.plist(5)` manual and
[Apple's launchd manual source](https://github.com/apple-oss-distributions/launchd/blob/main/man/launchd.plist.5).
The one-second throttle is a request, not an observed restart-latency guarantee.

The complete subprocess command family is:

```text
/usr/bin/plutil -lint B/C/LABEL.plist
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
ARMED now binds the plan hash; restart rejects a changed plan, readiness hash or
journal deadline before any target action. The original deadline is never extended.
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

Every CLI/ps/sysctl subprocess has a one-second timeout. Bootstrap capture has
a separate up-to-one-second child-kill/reap observation window. It terminates
only its retained CLI child on timeout/output overflow; a CLI death does not
prove registration or service absence. Polls are 50 ms; after
each termination action, at most five 100-ms postcheck intervals are attempted.
Readiness budget is three seconds, ownership must be observed by deadline minus
three, and final installer observation stops at armed time plus **25 seconds** per
case (up to 50 seconds for both, plus bounded in-flight observations/preflight).
Filesystem/hash/scheduling waits and launchd recovery are not hard real-time
bounds. The deadline triggers a stop attempt; this is explicitly **not a guaranteed
ten-second lifetime cutoff**. Any missed budget is incomplete, never a pass.

## Evidence and present validation

Both bootstrap calls first revalidate the sealed plan, exact plist dictionary/hash,
label absence, source/interpreter/plan/plist parent traversal and effective caller
access, and `plutil -lint`. At least three original seconds for guardian and five
for fixture must remain, including a recheck after fsyncing intent. These checks
do not certify launchd access. No permissions or domain are changed to obtain a pass.

For each role, exclusive **0400** `ROLE-bootstrap-intent.json` seals argv, plan/plist
hashes, path UID/GID/modes/flags and caller access observations before bootstrap.
Exclusive **0400** `ROLE-bootstrap-result.json` records exact argv, start/finish
monotonic times, actual CLI returncode (null if no process was created or reaped),
start/I/O errors, timeout/output-limit/cleanup flags and base64 raw stdout/stderr.
Capture drains both pipes without blocking, retains at most **65,536 bytes combined**,
and stops the retained CLI on a one-second timeout or excess output. Output seen
after the cap is not retained; observed byte count is not a total-output claim.
Partial bytes survive timeout; arbitrary non-UTF-8 bytes round-trip. Nonzero status,
any stderr, start/I/O/cleanup error, timeout or overflow fails closed. Status 0
alone does not prove the service ran. Abrupt SIGKILL/power loss may leave only
intent or a partial receipt; preserve that as incomplete. Intent collision refuses
replay even if the prior result is missing. No failed bootstrap triggers automatic
bootout, wider cleanup, permission repair, domain switch or a second case. An
already-armed guardian retains its original fixture deadline.

All new live evidence remains under `B`: `attempt.json`, then each case's
`plan.json`, two plists, `ready.json`, `guardian.jsonl`, `operator.jsonl` and
`result.json`; finally root `result.json`, or exclusive root `failure.json` on a
handled post-creation failure. Preserve all partial files on interruption. A
preflight refusal before root creation writes no new receipt. Live result may
claim only `CALIBRATED_HOST_FIXTURES_ONLY`, with VM containment **UNQUALIFIED**.

**15 v3 tests passed**, reusing all eleven frozen v2 regressions against the v3
helper. Four additional tests cover the exact complete plist for both roles in
both cases, missing/wrong/array session types despite a matching supplied hash,
extra plist keys during stopped-job verification, and exclusive root/label refusal.
Inherited checks retain raw binary diagnostics, CLI exit/stderr failures, timeout
partial output, stream cap, spawn denial, intent replay refusal, paths/plan/lint/
budget failures, interruption/restart, identity replacement and original deadlines.
Tests use mocks and trusted synthetic subprocesses; they never register launchd
jobs or start VMs. Live launchd admission/restart/forced termination remains
**NOT RUN**. All remaining metadata subprocesses retain v2's trusted finite-output
assumption with a one-MiB post-capture check; streaming caps apply to bootstrap.

The single authorization is consumed by invoking the pinned command once, even
if preflight refuses before root creation. Do not manually repeat it, choose a
new label/root, chmod/chown a plist/parent, switch to gui/system, enable a job,
use sudo, or perform repair under this authorization. Preserve all partial state
and report the command's exit status plus intent/result receipts for review.
Publication authorizes no execution. Approval must explicitly name calibration-v3,
the published source SHA-256, this procedure and its four labels/evidence root.

## Scope limit

Even successful host-fixture calibration would not qualify VM lifetime,
descendants, vmnet, network, filesystem or resource containment. No VM start,
production guardian, Container service change, #10, executable Faultline skill,
merge or issue closure is authorized. Those require separate qualification and
explicit effect authorization. Review and all candidate source hashes are in
[the v3 preparation record](2026-10-19-apple-container-guardian-calibration-v3-review.json).
