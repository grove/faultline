# Stage 1b setup-v2 — consumed attempt, recovery pending

**Do not run the startup command below.** The authorized setup-v2 attempt started
services, then failed Faultline's path comparison and recovery checks. Its receipt
is preserved unchanged. Only the [separate recovery proposal](APPLE_CONTAINER_RECOVERY.md)
is current; a startup retry requires a fresh identity and separate approval after
recovery is resolved. The remaining text records the consumed setup-v2 proposal.

The operator's setup-v1 receipt is [preserved byte for byte](2026-10-18-apple-container-setup-v1.json),
SHA-256 `e2fa363740ca780bd736f0daec8ed8f2e0c8bcf3621d0cbb5e9195a2b5ecfb1a`.
It reports `Background`, `startup_attempted: false`, `FAILED`, exit 1. Source
hashes match the reviewed script/TOML from PR commit `2c5b33b`. The rejection
was Faultline's Aqua-only guard, not evidence that Apple Container cannot use
Background. The [separate review](2026-10-18-apple-container-setup-v1-review.json)
distinguishes operator execution evidence from independent receipt/hash comparison.
Keep the original file, setup-v1 identity and all earlier evidence unchanged.
The previous authorization is consumed, including its recovery authority.

## Source conclusion and replacement safety checks

Apple Container 1.5.0 source is pinned to
`d265d669ecae041bf338cb3b39c4118316d138f0`:

- [ServiceManager](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPlugin/ServiceManager.swift)
  maps Background to `user/<uid>` and Aqua to `gui/<uid>` for registration and
  deregistration. The startup plist permits both session types.
- [SystemStart](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStart.swift)
  uses that mapping; it can fetch configured init despite kernel installation
  being disabled. Config copying, init and kernel pins remain as reviewed for v1.
- [SystemStop](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStop.swift)
  can stop all containers reached through its health/client connection and then
  enumerate prefix-matching services. A prefix-wide stop is unsuitable for scoped
  recovery across the shared user/GUI namespace. V2 does not call it.

**Background is a supported candidate for this limited setup**, subject to the
new checks below. This does not establish installed startup success or isolation.
No bootstrap-context switch, `asuser`, root session, sudo or sandbox relaxation
is introduced. The helper selects only the domain implied by its current manager.

Before startup, it reads `launchctl print system`, `launchctl print user/<uid>`
and `launchctl print gui/<uid>`. Any `com.apple.container.*` service **or endpoint**
in any of those domains blocks startup and recovery. This also checks the system
ancestor; user and GUI domains share Mach lookup names despite separate service
tables, as documented in this Mac's `/usr/share/man/man1/launchctl.1`.

The man page explicitly says `launchctl print` output is not a stable API. V2 is
restricted to this host's reviewed table shape, with a parser that rejects missing,
ambiguous or malformed tables instead of inferring an empty namespace. A read-only
calibration parsed all three current domains and found no Container names; this
is not a setup attempt or a lasting collision guarantee. The actual attempt
rechecks them. Missing/inaccessible domains block, including a headless host with
no readable GUI domain; this version does not add a fallback for other hosts.
Raw launchd dumps/environments are discarded, with only Container names retained.

## Historical setup-v2 command — authorization consumed

Working directory: `/Users/grove/projects/faultline`. Approve one execution of:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C /opt/homebrew/bin/python3 -I -B qualification/apple_container_service_setup.py setup-v2
```

The explicit `setup-v2` argument is required; the old no-argument command cannot
start a new attempt. It exclusively creates `evidence/setup-v2.json` and a fresh
`setup-v2` directory under `/private/tmp/faultline-apple-positive-v2`. Existing
files/directories stop the attempt. No signature/hardware recheck or Stage 1a
inventory rerun is included. Do not reset or discard the dirty working tree.

Reviewed SHA-256: helper
`8c01df30a82fc4f5b5c1d6eb734e61f5a9ca31932acbc854de203c0e8c4098a7`;
unchanged TOML
`ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e`.

The startup subprocess is exactly:

```text
/usr/local/bin/container system start --app-root /private/tmp/faultline-apple-positive-v2/setup-v2/runtime --install-root /usr/local --disable-kernel-install --timeout 15
```

Every subprocess has cwd `/`, closed stdin/unrelated descriptors, and only:

```text
HOME=/Users/grove
PATH=/usr/bin:/bin
LC_ALL=C
XDG_CONFIG_HOME=/private/tmp/faultline-apple-positive-v2/setup-v2/config-home
CONTAINER_APP_ROOT=/private/tmp/faultline-apple-positive-v2/setup-v2/runtime
CONTAINER_INSTALL_ROOT=/usr/local
```

The unchanged [TOML](apple-container-service.toml) pins init
`ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade`
(0.47.0, arm64/v8), and the Kata 3.32.0 kernel archive/member already recorded in
the historical v1 proposal. Kernel installation stays disabled. Private XDG config
is copied into the fresh runtime root; existing default config/kernel state is
not replaced. Custom/changed plugin guards, service 1.5.0/source/root checks,
copied-config comparison and exact-init metadata inspection remain in place.

The requested effects remain service registration/plists/runtime state, host
DNS/TLS/HTTPS to ghcr.io and its blob/CDN redirects for the pinned init, default
NAT creation, and loopback DNS listeners at `127.0.0.1:1053` and `:2053`.
Normal OS/runtime logs and registry credential lookup may occur; no secrets are
supplied/extracted and no login/admin prompt may be answered. No worker image,
kernel download, container/VM, canary, project or experiment #10 is authorized.

## Recovery, bounds and remaining limitations

After startup, observe Container services in the selected domain. A service is
eligible for automatic removal only if its **live launchd origin path** resolves
to a nonsymlink plist under this attempt's `setup-v2/runtime`, with matching label,
app root and install root. Record the plist SHA-256. Unknown/foreign ownership or
services appearing in another checked domain stop automatic recovery.

On startup/verification failure, first establish ownership for the whole observed
set. Immediately before each removal, recheck origin path and plist hash; only
then use this exact command shape for that recorded label:

```text
/bin/launchctl bootout user/<uid>/<owned-label>  # Background
/bin/launchctl bootout gui/<uid>/<owned-label>   # Aqua
```

There is no prefix-wide stop, wildcard, PID kill, cross-domain removal, pruning
or receipt deletion. Recheck all three domains afterward. Failed bootout, residual
registrations, changed identity or unreadable output means `INCOMPLETE_STOP_AND_REVIEW`;
leave uncertain services untouched and request scoped recovery. Registration
absence does not independently prove helper death or vmnet/DNS teardown.
API health is not proof that every NAT/DNS startup task succeeded.

**Keep all other Container management idle during setup/recovery.** Launchd has no
atomic compare-and-bootout operation; the ownership check does not claim protection
against another actor replacing a service between check and removal. If exclusive
management cannot be maintained, this attempt remains blocked. Coordinator death
can leave services behind; do not run a global stop from another session or repeat
setup. Review the recorded domain/identity before separately authorized recovery.

Budgets: zero VM/workload allocation; one client at a time; 120 s startup outer
timeout, 15 s each post-start status/init inspection, 5 s per launchctl call.
At most 16 relevant services per domain and 16 endpoints per domain; at most 16
owned targets can be removed. Maximum summed subprocess waits including a late
failure and recovery are 515 s, excluding filesystem/scheduling delays. Each
ordinary output stream retains at most 64 KiB; launchd stdout has a 4-MiB temporary
parse bound and is not retained. These bounds are checked on trusted CLI capture,
not live output quotas. Host service CPU/RAM/disk still have no hard quota; no VM
budget increase is granted. Init metadata is not verified payload or qualification.

Success leaves owned services registered, with the new receipt containing manager,
domain, source hashes, exact observations and owned plist identities. It authorizes
neither later provisioning nor synthetic execution. Keep PR #17 draft and issue #2
open. All such execution remains **NO_GO / UNAVAILABLE** pending separate approval.
