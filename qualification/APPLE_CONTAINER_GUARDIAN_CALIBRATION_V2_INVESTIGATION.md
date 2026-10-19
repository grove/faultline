# Calibration-v1 bootstrap investigation — cause undetermined

V1 is **CONSUMED FAILURE; DO NOT REPEAT**. PR #17 remains draft, issue #2 open,
Faultline execution **NO_GO / UNAVAILABLE**. This investigation used disk reads,
plist lint, installed manuals and Apple documentation. No bootstrap, process/log
query, Container operation, installation or VM launch was run.

## What the evidence establishes

The [new outcome record](2026-10-19-apple-container-guardian-calibration-v1-outcome.json)
separates operator observations from independent offline review. The preserved
`failure.json` names the first guardian `launchctl bootstrap user/501` invocation.
The helper raised on either a nonzero exit **or any stderr** and discarded both
streams and the exit status. It is therefore unknown whether launchctl returned
nonzero, emitted stderr with status zero, or what launchd reported. Do not invent
an errno or treat a guessed error string as evidence.

The original root has attempt/failure receipts and only the first case's plan and
two plists. No readiness, guardian/operator journal or second case is present.
The five file copies in [the evidence directory](guardian-calibration-v1-evidence/)
are byte-identical to the live originals, with hashes, original modes and owners
in the outcome manifest. No original bytes, modes, names or directories were changed.

The operator reports no matching UID-501 v1 process (`pgrep` status 1), no matching
last-hour launchd log rows beyond the column header, successful lint for both
plists, and absent first-case labels (`launchctl print` status 113). Exact log-query
argv and raw operator outputs were not supplied. These are later observations,
not evidence of the launchd transaction or a particular acceptance failure.
Independent read-only lint of both preserved plists also returned status 0.

## Requirements checked

The installed manuals are retained in [this pinned snapshot](guardian-calibration-launchd-docs/),
including path modes, ACL listing and inspection provenance. `launchctl.1` SHA-256
`cf8752dd8eb8c3370c7d03b333430aa68a665c907c475ea407cb1b6542083ae2`
matches the earlier setup-v1 review pin. `launchd.plist.5` SHA-256 is
`1c5f5041c1d3492988bfa6f9dc6d969dfd072d20af2703c28d9a8f6ed6aaadcb`.
Line references below refer to these exact raw manual files.

| Area | Documentation and observation | Conclusion for v2 |
| --- | --- | --- |
| Plist syntax and job definition | Both files lint successfully and contain a string Label, string-array ProgramArguments and expected launch keys. `launchd.plist.5` lines 181–216 define Program/ProgramArguments. | Lint does not validate launchd semantics, domain policy or executable startup. V2 also compares the full dictionary with its exact generated job before each bootstrap. |
| Ownership and permissions | `launchctl.1` lines 464–475 document ownership by installation location and prohibit group/world writes in the legacy load section. V1 files are UID 501, GID 0, mode 0400, single-link regular files. | No cited requirement mandates 0644 or world readability for this temporary user-domain path. Keep 0400; do not claim permission failure or loosen modes as a speculative fix. The legacy-location guidance is not a complete modern bootstrap acceptance specification. |
| Accessible parent directories | Evidence root and case are 0700 UID 501. `/private` is 0755, `/private/tmp` is sticky 01777. `/Users/grove` is 0750 UID 501; its observed ACL denies deletion, not traversal. All inspected parents are searchable by this caller now. | Execution needs search access through parents and read access to source/plan/plist; mode bits alone do not cover ACLs, sandbox/TCC or launchd's context. V2 records/checks effective caller access for every parent; this is a preflight observation, not proof of launchd access at the earlier failure. No parent chmod/chown. |
| Executable and source paths | The resolved Homebrew launcher and framework process executable both match v1's pinned hashes; their paths are absolute. The launcher is executable, source readable by this caller. `launchd.plist.5` lines 181–216 allow argv[0] to supply the executable when Program is absent. | No evidence requires adding Program, using a shell, moving the source, installing Python or changing PATH. V2 keeps the pinned executable and exact isolated Python arguments, and checks both executables plus parent paths. |
| Bootstrap domain | `launchctl.1` lines 38–69 distinguish user and GUI domains; lines 96–108 describe bootstrap with plist paths. User domains can exist independently of GUI login, and GUI/user service inventories differ. The v1 code reached bootstrap only after its Background-manager check. | `user/501` is documented syntax; that alone does not establish current authorization/acceptance. Keep UID 501, Background check and successful exact-domain inventory. Do not switch to gui/501, system, sudo or alter enable/disable state. |
| Arguments, environment and working directory | Each argv element is separate: pinned Python, `-I`, `-B`, absolute source, exact role, absolute plan. WorkingDirectory is `/`; PATH/locale/timezone are explicit. No shell expansion, relative interpreter, UserName/GroupName override or external input. | V2 retains this form and checks the complete plist before bootstrap, then actual origin/program/argv/PID when observing registration. A successful bootstrap is separate from successful exec/readiness. |

The source bytes and executable pins are unchanged from those bound in the v1
plan; the inspection JSON records current path details. These observations cannot
reconstruct earlier launchd access, transient policy, disabled-state handling or
job admission. We did not change those settings or run diagnostic bootstrap probes.

The previously linked [Apple OSS manual](https://github.com/apple-oss-distributions/launchd/blob/main/man/launchd.plist.5)
was inspected as historical context, not assumed to match this installed OS.
[Apple's archived guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
explains labels and tokenized arguments and offers standard job logging examples.
Its installation examples do not establish the cause of this temporary-path
bootstrap failure. V2 captures the bootstrap CLI's pipes directly; it does not
enable global debug logging or create unbounded service log files.

## Reviewed correction and limits

V2 is a versioned copy preserving v1 history and its identity-scoped recovery.
Both bootstrap call sites use the new exclusive intent/result capture. They
retain bounded raw bytes, actual exit status and explicit timeout/output-limit
flags, including launch failure and partial timeout output. No automatic bootstrap
retry occurs. A missing/partial result after abrupt death remains incomplete.
The same four-role/case structure, fixed ten-second original deadlines, exact-target
termination and evidence-preserving cleanup remain. Restart now also binds ARMED
to the plan hash and checks the prior deadline/readiness hash before proceeding.

All v2 behavior is tested with mocks and trusted synthetic subprocesses. A future,
separately approved live run may still fail launchd admission and must retain its
new diagnostics without repair or retry. Even successful host-fixture calibration
cannot qualify VM descendants, file/network isolation, resource enforcement, #10
or executable Faultline behavior.
