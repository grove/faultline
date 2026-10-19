# Guardian calibration-v4 — prepared, approval required

V3 admitted both first-case jobs and forced the fixture stop 0.281108 seconds
after its original deadline. The installer failed before coordinator SIGKILL;
coordinator-loss failed and guardian-restart never ran. This is not an overall
calibration success. See the [original outcome](2026-10-19-apple-container-guardian-calibration-v3-outcome.json).

The retained evidence cannot determine either operand of the compound parent
identity check. Initial coordinator PID/UID/birth/executable, subsequent identity,
poll result/returncode and parent observation time were discarded. Coordinator
stdout/stderr went to DEVNULL. The successful fixture bootstrap predates OWNED;
it does not prove later survival. Startup executable transition, coordinator exit
and deadline/observation race remain hypotheses for v3.

V4 preserves the v3 helper as frozen history. The fresh helper first durably logs
spawn and early parent observations, then waits for a sealed coordinator-ready
receipt binding PID/UID/birth, the exact pinned framework executable and plan hash.
Parent independently matches this identity before binding. Early launcher identity
is diagnostic only and cannot authorize a kill. Every identity after binding must
match exactly. The child also seals fixture-bootstrap completion. Both parent
process inspection and Popen.poll are recorded unconditionally with monotonic
start/end times, even if inspection fails. A later mismatch or premature exit
fails closed. This addresses a source-verified startup-order weakness without
claiming it caused the historical failure.

The parent drains nonblocking stdout/stderr into a combined 65,536-byte cap;
fsynced 0600 coordinator.jsonl contains output deltas, identity observations, poll
status and times. Exclusive 0400 spawn intent and final result include argv, PID,
raw base64 output, error and actual returncode (null if still alive/unreaped).
Overflow or unavailable identity fails. On handled failure no uncertain identity
is killed; the trusted coordinator has a 30-second alarm set on entry. The
launchd guardian retains its original fixture deadline. Abrupt installer death
can leave an intent/partial result; no result means incomplete, never a pass.

The executable source is `qualification/apple_container_guardian_calibration_v4.py`,
SHA-256 `522c8b79c86edb5b48e087b848a029b4a88b1f1ef23f498597f2561ce10cbc1c`, in the commit containing this document. A separate native
approval request must name the commit and source hash. Its wrapper reads the
absolute path under `/private/tmp/faultline-qualification-20261019`, verifies this
hash and compiles/executes those same bytes with the absolute `__file__` and argv
`install-calibrate-v4`. Existing `/opt/homebrew/bin/python3 -I -B`; cwd `/`;
environment `PATH=/usr/bin:/bin`, `LC_ALL=C`, `TZ=Europe/Oslo`.

Prerequisite: all four v3 labels absent, with stopped v3 registration recovered
under its separate approval or positively absent. All fresh v4 labels and the
fresh root must be absent. Invocation consumes approval even on preflight refusal.

The exclusive new evidence root is `/private/tmp/faultline-guardian-calibration-v4`.
Only these labels may be registered/targeted, all in **user/501**:

```text
dev.faultline.guardian-calibration-v4.coordinator-loss.guardian
dev.faultline.guardian-calibration-v4.coordinator-loss.fixture
dev.faultline.guardian-calibration-v4.guardian-restart.guardian
dev.faultline.guardian-calibration-v4.guardian-restart.fixture
```

For each case, fsync exclusive 0400 plan/plists/readiness and original monotonic
deadline exactly armed+10 seconds before bootstrap, in 0700 host-only directories.
Both jobs retain string LimitLoadToSessionType=Background, ProcessType=Background,
RunAtLoad and ExitTimeOut=1. Guardian retains KeepAlive={SuccessfulExit:false},
ThrottleInterval=1. Exact program arguments remain pinned Python, -I, -B, absolute
v4 helper, role, absolute case plan. Original [v3 procedure](APPLE_CONTAINER_GUARDIAN_CALIBRATION_V3.md)
describes the unchanged identity, bounded bootstrap capture, plan/readiness/journal
provenance and independent termination rules; the v4 source supplies the exact
fresh paths and added coordinator diagnostics.

Effects: two sequential cases, each at most one trusted coordinator, guardian and
nonforking host fixture. Four one-time bootstraps total. After ownership and sealed
bootstrap completion, independently verify and SIGKILL the retained coordinator
before original deadline minus three seconds; verify returncode -SIGKILL and PID
absence. In the second case only, verify guardian identity twice, journal intent
and SIGKILL its exact launchd target within the same original budget. Launchd must
restart it with a new observed PID and the unchanged original deadline. At deadline
the guardian uses exact fixture bootout, with one revalidated exact-target SIGKILL
fallback only if necessary. Require durable BOOTOUT_INTENT and TERMINATED after
the original deadline and before OWNED+29 seconds, excluding the fixture's 30-second
cooperative alarm as a passing oracle. Independently recheck captured fixture PID
and registration absence, guardian PID(s) absence and stopped guardian registration
identity; bootout only that exact stopped guardian, then verify absence.

Every metadata/action command is bounded to one second. Bootstrap retains v3's
stream cap and extra up-to-one-second retained-CLI kill/reap budget. Readiness is
three seconds; coordinator startup must bind before deadline-5, ownership/injection
before deadline-3; final observation ends at armed+25 per case (50 seconds for both
plus bounded in-flight preflight/observations). Expected wall time under 60 seconds;
filesystem hashing/scheduling is not a hard real-time guarantee. The deadline
triggers host stop and measured latency is recorded, not an instantaneous cutoff.
No network, VM, guest or Container service operation. No workload CPU/memory stress;
only three small Python helpers per active case, plus transient metadata CLIs.

Refuse changed identity/source/interpreter/provision receipt/boot/plan/readiness/
plist/session, collisions, unavailable observation, torn/malformed journal,
insufficient original time, premature coordinator exit, output overflow, failed
bootstrap or shutdown, replaced PID, unregistered live PID, missing restart or
independent absence. Preserve partial state, stop before the next case, never retry
or recycle an attempt identity. No automatic recovery of a failed registration.
No evidence deletion or permission change.

Approval covers only this host-fixture stage. It excludes v3 recovery, production
guardian, setup/provision/download, existing Container services, VM/guest/canaries,
#10, Faultline skill activation, sudo/domain switch, broad process termination,
merge and issue closure. Even CALIBRATED_HOST_FIXTURES_ONLY leaves execution
NO_GO / UNAVAILABLE until separate VM and boundary qualification.
