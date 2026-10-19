**Current decision:** [Terminal supported-interface NO-GO](APPLE_CONTAINER_VM_TERMINAL_NO_GO.md), with the [updated control matrix](2026-10-19-apple-container-vm-control-matrix-v2.json) and offline-tested immutable binding. The review below is the preserved initial disposition at commit `4d2c7be`. No calibration was repeated.

# VM-specific qualification — NO_GO after successful host-fixture calibration

Host-fixture calibration-v4 succeeded on macOS 27.0.1 / 26A434, arm64, UID 501.
The [independent verification](2026-10-19-apple-container-guardian-calibration-v4-independent-verification.json)
confirms coordinator death, guardian restart with the original deadline, forced
fixture stops, and absence of all eight captured PIDs and all four registrations.
The [outcome](2026-10-19-apple-container-guardian-calibration-v4-outcome.json)
contains measured deadline latency. This prerequisite does not qualify a VM.

The existing positive stage and VM guardian were inspected, without launching
Container, changing services, creating a VM configuration, running guest Python or
canaries, or executing #10. The four existing services retain their original
setup-v4 PIDs, UID/birth, plist and binary hashes. The prospective container root
is absent. No live VM approval is ready under the current observation contract.

## Source findings and counterevidence

The existing [VM guardian](apple_container_guardian.py) binds the prospective runtime
`user/501/com.apple.container.container-runtime-linux.faultline-apple-positive-v3`
to its origin, argv, binary, PID, UID and birth. Its `observe` and `watch` functions
can observe only that registration and PID. `TERMINATED` checks no VM backend,
auxiliary process, device or network-session identity. The prepared plan binds
container ID, target and source, but the implementation does not seal/verify the
created VM configuration and artifact references at each ownership/action boundary.
The separate positive coordinator/marker extraction is still a proposal.

[Apple DTS guidance](https://developer.apple.com/forums/thread/848542) says the OS
is expected to clean up a Virtualization client's VMs after the client crashes,
and recommends relying on that lifecycle behavior while testing for leaks.
This is useful architectural support, not a measured deadline or independent
observation on this host. The same answer says helper identities and relationships
are implementation details, some helpers are per-user, and no direct supported
VM-to-execution-owner diagnostic is available. Therefore a process-name sweep
cannot establish VM-specific ownership, and deleting every remaining helper
would risk unrelated VMs. This review does not claim that an orphan VM actually
exists, or that Virtualization's normal cleanup is broken.

The installed `/usr/share/man/man1/launchctl.1`, lines 291–300, describes procinfo
as a root-only diagnostic whose output is unsuitable as a production contract.
The [host receipt](2026-10-19-apple-container-guardian-calibration-v4-host.json)
pins its SHA-256. No procinfo invocation, sudo, private API or privilege change
was attempted. More privileges alone would not provide the missing stable contract.

Pinned [RuntimeService.swift](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/RuntimeLinux/Server/RuntimeService.swift#L1300)
catches a container-stop error, closes forwarders/network sessions and releases
waiters. The watcher cannot treat CLI/metadata completion as an independent proof
of successful VM stop. Pinned [LinuxContainer.swift](https://github.com/apple/containerization/blob/bc994b88df46207fad7775b0eabc51947e315881/Sources/Containerization/LinuxContainer.swift#L929)
attempts guest/relay cleanup and VM stop; this source path is useful but is not
execution evidence after abrupt client death.
Pinned [VZVirtualMachineInstance.swift](https://github.com/apple/containerization/blob/bc994b88df46207fad7775b0eabc51947e315881/Sources/Containerization/VZVirtualMachineInstance.swift#L195)
performs stop through its in-process VZVirtualMachine object. Its VM configuration
maps explicit interfaces and read-only share options, but no independent
out-of-process VM-liveness or network-teardown receipt is exposed here.

## Reproducible offline disposition

At the published candidate, run only the trusted offline tests:

```text
/opt/homebrew/bin/python3 -I -B -m unittest discover -s tests -p test_apple_container_guardian.py
```

All four pass with mocked runtime-owner observations. Their passing assertions
cover one owner and the fixed deadline, not auxiliary execution, vmnet, mounts,
network denial or aggregate resources. Read `process`, `observe`, `watch`, `job`
and `main` in the prepared guardian to reproduce the missing observation/binding
surfaces. Its job also lacks the Background session key now validated by the
separate host calibration, and its journal protections do not match v4. No frozen
provisioning source was modified to hide these gaps.

The [matrix](2026-10-19-apple-container-vm-qualification-no-go.json) separates
observed host calibration, source predictions and NOT RUN controls. No experiment
or fixture was added to compensate for missing enforcement. Worker provisioning
remains consumed success; its full sparse snapshot was not rehashed in this stage.

The next necessary work is a supported VM-specific ownership/liveness and teardown
observer/recovery contract, plus a versioned completed coordinator/configuration
binding, offline-tested before any live request. With the presently prepared
interfaces this contract cannot be substantiated. A future bounded VM-creation,
bootstrap/guest, owner-loss and teardown procedure needs its own explicit native
approval; there is no request to approve an incomplete VM stage now. Filesystem,
private-path, network and aggregate-resource controls would still need separate
qualification. Execution remains **NO_GO / UNAVAILABLE**, PR #17 **draft**, issue
#2 **open**, #10 **frozen / NOT RUN**, and the Faultline skill **advice-only**.
