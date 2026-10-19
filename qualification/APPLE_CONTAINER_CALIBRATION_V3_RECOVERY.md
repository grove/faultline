# V3 stopped-registration recovery — prepared, approval required

This is a separate one-time host effect from calibration-v4. Original v3 is a
consumed failed calibration. See the [outcome](2026-10-19-apple-container-guardian-calibration-v3-outcome.json).
The [current independent observation](2026-10-19-apple-container-guardian-calibration-v3-current-state.json)
finds the exact stopped registration, source and plist intact; captured guardian
16954 and fixture 16969 are absent. Fixture and both second-case labels are absent.
These observations must be re-established immediately before action.

The executable candidate is `qualification/apple_container_calibration_v3_recovery.py`,
SHA-256 `001c1768021e30d3c0fe9a1877e838ffbf0e052916215d4fde384371208071c9`, in the published commit containing this document.
The native approval request will identify that exact commit and execute a wrapper
that reads this path in `/private/tmp/faultline-qualification-20261019`, verifies
this hash, then compiles and executes those same bytes with
`__file__` set to that absolute path and argv `recover-stopped-v3-once`.
Use existing `/opt/homebrew/bin/python3 -I -B` with environment
`PATH=/usr/bin:/bin`, `LC_ALL=C`, `TZ=Europe/Oslo`, cwd `/`.
No installation, service startup or network call is needed.

The sole host action is:

```text
/bin/launchctl bootout user/501/dev.faultline.guardian-calibration-v3.coordinator-loss.guardian
```

Before action, verify UID 501, exact user/501 domain, original source SHA-256
`2c431ec7b99a6424eee8b7b7fcbff1eaf1c2b28fa2503b8a804ef587827ecc02`,
sealed plan/readiness/boot identity, both pinned Python executables, and complete
original tree membership, file hashes, ownership, group, modes, inode/device,
link counts, flags, modification and change times against the hash-pinned manifest.
The plist SHA-256 must remain
`23bc939534ac5762fea03f33dbc898683808e7949c5a31825301e843933c4c62`.
Both complete generated plist configuration and live source/program/arguments/origin
must match. Require stopped state with no live PID, independent absence of captured
16954/16969, and absence of fixture/second-case registrations. An unregistered live
process is a refusal, never treated as a stopped registration.

Create exclusively `/private/tmp/faultline-guardian-calibration-v3-recovery-01`
(mode 0700), with fsynced exclusive 0400 before, intent, action, after and result
receipts, or preserved failure. If already absent, record no action. Revalidate all
identities before a single bootout. Capture actual status and bounded raw output
(up to 64 KiB combined), including timeout partial output. One-second subprocess
limits; expected total below 20 seconds, observation/filesystem scheduling is not
hard real time. Independent postcheck must find registration and captured PIDs
absent and original tree unchanged. No retries or second bootout on failure.

Approval authorizes only removal of this exact stopped registration and creation
of that new receipt directory. No signals to processes, bootstrap, v4 execution,
VM/guest/canary/#10, Container service change, deletion, permission change, sudo,
domain switch, broad cleanup, merge or closure. Failure preserves original and
new evidence for review. Approval is consumed by the single invocation.
