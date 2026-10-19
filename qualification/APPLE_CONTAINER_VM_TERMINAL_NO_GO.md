# Terminal VM feasibility decision for the pinned Apple stack

**TERMINAL NO_GO for the present ownership and independent-teardown requirements.**
No VM-stage approval is requested. This conclusion applies to Apple Container
1.5.0 at `d265d669ecae041bf338cb3b39c4118316d138f0`, Containerization 0.47.0 at
`bc994b88df46207fad7775b0eabc51947e315881`, and the audited public SDK 27.0 APIs.
It is not a claim that Virtualization leaks VMs or that every Apple backend is
incapable of satisfying a different contract.

Host-fixture qualification is complete and was not repeated. Recovery and v4
authorizations remain consumed. No VM creation/bootstrap, guest, canary, #10,
challenge, service operation or private/root-only diagnostic occurred here.

## What the supported interfaces actually establish

| Interface | Instance-specific support | Missing required property |
| --- | --- | --- |
| `VZVirtualMachine.state`, delegate, `stop(completionHandler:)` | A holder of the VM object can inspect its state and receive stop success/error. A nil stop error means success; conflicting state transitions may return errors. | No public external lookup/adoption handle for the running instance, authenticated execution-backend identity, or bounded completion time. |
| Runtime XPC / Container snapshots | Configuration ID maps to one runtime service; source binds root and `--uuid` to the configuration ID. | Runtime status and cleanup messages come from the component being supervised; they do not independently attest actual guest/backend execution after that component dies. |
| Apple network XPC `lookup(hostname:)` | The allocation table can be queried by hostname. Allocations are associated with a persistent client session and released on disconnect. | An allocation lookup is not a VM-liveness or kernel-interface teardown oracle, and no release-completion deadline is exposed. |
| vmnet `interface_ref` / stop callback | A holder can stop I/O on that interface; the immediate return schedules completion. | A UUID is not an externally adoptable interface handle or a VM-to-interface binding. Network serialization transfers a network reference, not the particular interface or VM execution instance. |
| No-network configuration | Empty attachments produce no interfaces/network allocation in the pinned runtime loop. | This is a source-grounded configuration fact; actual device/IPC absence has not been independently observed. It does not repair the missing VM execution oracle. |

The [API evidence catalog](2026-10-19-apple-container-vm-supported-api-evidence.json)
pins 23 source files and five installed public headers, with exact paths, hashes,
symbols and line locations. The [current control matrix](2026-10-19-apple-container-vm-control-matrix-v2.json)
records source support separately from host observations and UNAVAILABLE controls.

Primary references: [VM object API](https://developer.apple.com/documentation/virtualization/vzvirtualmachine),
[stop API](https://developer.apple.com/documentation/virtualization/vzvirtualmachine/stop(completionhandler:)),
[vmnet stop API](https://developer.apple.com/documentation/vmnet/vmnet_stop_interface(_:_:_:)),
and [pinned network allocation implementation](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/Network/Server/DefaultNetworkService.swift).
The SDK declarations were inspected directly; no API was invoked on a VM or network.

## Teardown contract and its limit

[Pinned RuntimeService cleanup](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/RuntimeLinux/Server/RuntimeService.swift)
catches stop errors, closes forwarders and network sessions, and releases waiters.
Its status cannot replace independent VM teardown observation.
[Containerization's stop path](https://github.com/apple/containerization/blob/bc994b88df46207fad7775b0eabc51947e315881/Sources/Containerization/LinuxContainer.swift)
attempts guest/relay cleanup and calls the VM object's stop method.
Those are inspectable normal-cleanup paths, not independently observed results
when the runtime itself is killed.

[Apple DTS](https://developer.apple.com/forums/thread/848542) supports relying on
system cleanup of a Virtualization client's VMs after client death. It also
explains that helper identities/relationships are implementation details, some
helpers are per-user, and no direct supported execution-owner mapping is available.
That is substantial architectural counterevidence to assuming an orphan. It
supplies neither a host-specific deadline nor the required independent teardown
receipt. A helper process can remain for legitimate shared-service reasons;
its presence or name alone proves neither guest survival nor ownership.

The public VM object offers state to its holder, not an external VM registry.
Saved-state restore creates/resumes a separately controlled execution context;
it does not adopt a live instance after client death. `requestStop()` asks the
guest to stop and cannot enforce the host deadline. An in-runtime state/stop
telemetry extension would help normal operation but disappears with the owner;
a signed message from it would not close the independent-observer gap.

No process-name inference, root-only `launchctl procinfo`, private selector or
system-wide helper termination is proposed. Merely extending a timeout cannot
create the missing ownership capability. No observed VM leak is alleged.

## Safe offline implementation completed

[apple_container_vm_binding.py](apple_container_vm_binding.py) implements the
parts that can be bound and checked without contacting the runtime:

- Exact reviewed `runtime-configuration.json` bytes, creation identity, fixed
  scope and artifact paths. The create output references kernel/init/rootfs;
  `config.json` and copied bundle artifacts are produced later during bootstrap.
- Published kernel, init, worker sparse-content, runtime/Python, synthetic input,
  guest-source and consumed provisioning-receipt pins. New guardian/coordinator
  source hashes must also be supplied as reviewed inputs. Parent symlinks,
  hardlinks, changed identity, group/world write and excessive files are refused.
- Exclusive fsynced 0400 plan persistence in an existing host-owned 0700 directory,
  one plan hash shared by both participants, exact startup argv/PID/UID/birth/
  executable, boot identity and the unchanged armed+10 monotonic deadline.
- Later bundle configuration/kernel/rootfs metadata and copy-content checks,
  plus runtime plist/origin/argv/binary and independent runtime-PID binding.
- Strict journal provenance and preservation on coordinator loss, guardian loss,
  uncertain identity, incomplete teardown and deadline expiry. Replay cannot
  renew the deadline or record an invented successful VM termination.

The code is an offline contract, **not a runnable VM coordinator or production
guardian**. The earlier positive-stage “coordinator” was prose plus the frozen
guest acknowledgement fixture, not an implemented host runner. The shared binding
and role checks are now implemented and tested; no live adapters were created
past the terminal decision gate. File hashes are content seals and revalidation,
not an atomic check/use lease or filesystem-enforced immutability. Sparse-copy
structure differences fail closed even if logical contents might be equivalent.
Large hashing work has not been qualified inside a ten-second live deadline.

The disposition always returns `TERMINAL_NO_GO`, no host actions, no execution
authority, no teardown proof and no retry. A supplied runtime-absence record,
valid participants or mock “success” cannot make the missing public oracle pass.
Existing frozen guardian, guest, provisioning code and calibration evidence were
left unchanged. No real instance plan or artifact rehash/provision attempt ran.

Validation: **141 offline tests pass**, including ten new binding tests. They
exercise configuration/artifact/copy tampering, missing pins, unsafe paths,
participant and runtime replacement, exclusive receipts, startup/readiness,
boot/clock/deadline changes, loss/restart replay, interrupted journals and refusal
to turn owner absence into VM teardown. Synthetic files and observations only.

## Maintainer decision required to proceed

Choose an architectural direction; neither is authorized by this report:

1. **Keep this stack disabled and obtain an Apple-supported external instance
   control/observation contract.** It must cover actual VM execution after owner
   loss, bounded termination and instance-specific auxiliary/network disposition.
   Another statement of expected crash cleanup alone does not meet this requirement.
2. **Authorize evaluation of a different ownership boundary.** A separately
   supervised VMM process with documented execution ownership and independently
   inspectable process/network containment is the credible direction—for example,
   a dedicated Linux KVM process within a scoped cgroup/network namespace. It
   would need its own threat model and full qualification. Retaining Apple Silicon
   via a new direct Hypervisor.framework owner is a larger new-runner project,
   not a correction to Apple Container. [Apple's Hypervisor model](https://developer.apple.com/documentation/hypervisor)
   documents process-owned VMs, but does not qualify such a runner or its devices.

No scope relaxation is proposed. There is no safe approval-ready first-VM stage
under the current contract. PR #17 remains draft, issue #2 open, #10 frozen and
Faultline execution disabled. The next decision is architectural, not permission
to rerun calibration or collect another set of process-name logs.
