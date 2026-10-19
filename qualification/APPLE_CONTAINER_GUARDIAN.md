# Minimal guardian for the later positive stage — prepared only

`apple_container_guardian.py` is trusted host code, never mounted into the guest.
Provision-v1 does not invoke it or register a guardian job. It is not a sandbox
qualification result or a complete positive-test coordinator. Its source and state
transitions are tested with mocks; live launchd/Virtualization lifetime calibration
is still unobserved. Only the separately reviewed positive stage may exercise it.

The later request will reuse the frozen positive-v2 fixture and immutable synthetic
inputs, with fresh name `faultline-apple-positive-v3` and fresh host-only evidence.
It must first prove that name, metadata root and runtime launchd label absent, then
`container create` the exact reviewed configuration. Pinned ContainersService.create
writes runtime configuration and gets snapshots without bootstrapping a VM. It must
freeze that new configuration, artifact hashes and creation identity before start.
No target project or altered guest fixture is introduced.

Before **any bootstrap**, write a sealed, host-only plan containing container ID,
target, guardian source SHA-256, armed host monotonic time and an absolute monotonic
deadline no more than ten seconds later. Generate the guardian launchd plist with
`job(plan_path, plan_sha256)` and register that one new job in user/501. Its RunAtLoad
job has `KeepAlive: {SuccessfulExit: false}` and one-second restart throttling, so
coordinator or watchdog death does not start a new deadline. The coordinator must
wait for the fsynced `guardian-ready.json` for this exact plan and enough remaining
time; otherwise it must not bootstrap. The plan/journal/evidence are never guest
mounts. No deployment/registration command is authorized now.

Source grounds the mapping rather than assuming the word UUID means a random ID:
[ContainersService.registerService](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/ContainerAPIService/Server/Containers/ContainersService.swift)
passes the configuration ID as both `--uuid` and instance ID, with the container
root. [PluginLoader](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPlugin/PluginLoader.swift)
writes its origin at that root's `service.plist`. The guardian verifies actual live
registration/origin, exact root/UUID arguments, app/install roots and binary bytes,
then records the VM-owner runtime PID, UID, executable, birth time and plist hash.
The exact future target is
`user/501/com.apple.container.container-runtime-linux.faultline-apple-positive-v3`;
its executable is pinned to SHA-256
`e8bee184cc1f6b53982f9cc4ecb02085ebe238b8834112f71f8972c0d488511a`.
No current setup-v4 service target is eligible for termination.

The host watchdog owns the deadline, independently of the fixture's eight-second
alarm, stdin acknowledgement, CLI lifetime or coordinator heartbeat. On deadline
it rechecks frozen service/PID/birth ownership, records/fsyncs the action and uses
only that exact target's `launchctl bootout`. If that fails/times out and the same
service and process still exist, the sole fallback is `launchctl kill SIGKILL` for
that exact target, again after identity revalidation. No global stop, name-based
process kill, bare PID kill or metadata deletion. Journal replay preserves the
original deadline/owner and does not repeat a recorded bootout or kill.

`launchctl`/targeted `ps` observations are each timed out at one second. The ten-
second deadline triggers termination; local observation/scheduling and identity-
checked termination add latency. It is not a claim of an instantaneous ten-second
VM lifetime cutoff. At most three seconds of timed command waits occur per ordinary
owner observation, two one-second termination commands and ten final bounded
postchecks; filesystem hashing/scheduling and launchd restart delays remain outside
those command bounds. The later positive request must explicitly accept its full
stop/observation window; this source alone does not authorize a changed VM budget.

Successful termination requires both runtime registration absence and an independent
targeted ps observation that the captured VM-owner PID is gone. Stopped CLI metadata
or guest exit text alone never passes. A remaining PID, replacement identity,
inaccessible observation or failed termination records `INCOMPLETE_STOP_AND_REVIEW`,
leaves foreign/uncertain identities untouched and forbids another run. The watchdog
does not claim independent observation of every Virtualization.framework auxiliary
process or complete vmnet teardown; that remains a qualification gap.

The later positive coordinator must retain start/configuration/guardian observations,
copy and host-verify the frozen 26-byte tmpfs marker before acknowledging the guest,
and independently observe termination on normal exit, timeout and coordinator loss.
It may only delete owned stopped metadata after proving termination, under that
later authorization. This provisioning request neither creates that VM nor declares
the eventual positive stage ready to run without review of its completed artifact
receipt and exact coordinator/guardian plan.
