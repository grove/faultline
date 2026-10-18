# Stage 1b: initial service setup — approval required

Stage 1a is complete and stopped at **unregistered**, not a containment failure.
The [unaltered inventory](2026-10-18-apple-container-inventory.json) has SHA-256
`801d606d2816c1ca63658edc1259edb71e7f7b83e741a16c605955c1e5f3f2b9`.
It reports status exit 1, no image listing, no kernel inspection and no requested
boundary launch. The accidental second invocation refused the existing receipt
before its subprocess loop. Do not delete, overwrite or rerun that inventory.

Execution/timing and the repeat traceback are **operator-supplied evidence**.
Independent current-byte comparison finds the local helper identical to the file
in reviewed PR commit `9ad0f52ad58ceda935d5ba7dd4b8d9ddbece007a` and its prepared-v2
source hash. Local HEAD remains `ad4b3db108fa9e7c5c5035a0d26f4c09eb9647c6` with local
changes. This reconciles current file identity; the inventory did not record a
script hash at invocation, so execution-time identity is **corroborated, not
independently attested**. See the [provenance review](2026-10-18-apple-container-inventory-review.json).
Neither checkout was reset or cleaned. Prior frozen sources/receipts remain intact.

## Exact next authorization

Approve **only the fixed setup helper and its failure recovery**, from cwd
`/Users/grove/projects/faultline`, in the operator's normal Terminal:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C /opt/homebrew/bin/python3 -I -B qualification/apple_container_service_setup.py
```

Use the reviewed helper/config bytes from this PR, not a commit label alone.
The helper records both source hashes in its new receipt. It is a one-attempt
setup procedure, not a general runner. Run no other Container commands during
setup/recovery: startup uses Apple's shared per-user service labels even with a
dedicated data root. No signature/hardware checks or Stage 1a rerun are included.

Reviewed SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `apple_container_service_setup.py` | `6d8e6060b64ebab3913ad5730bf6f0d13c7d18ee7efce91e645133385f266d20` |
| `apple-container-service.toml` | `ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e` |

The fixed [configuration](apple-container-service.toml) sets init to
`ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade`
(Containerization 0.47.0, arm64/v8). Kernel configuration pins Kata 3.32.0 archive
SHA-256 `8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5` and member
`opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug`; **kernel installation is disabled**.
No existing default kernel/config is replaced: all writes target a new `setup-v1`
under `/private/tmp/faultline-apple-positive-v2`. An existing setup directory or
receipt is a stop, never a repair/retry permission.

The helper requires launchctl manager `Aqua`, then checks `/bin/launchctl list`
without activating services. **Any existing `com.apple.container.*` label aborts
before registration or shutdown.** It creates its private config and invokes:

```text
/usr/local/bin/container system start --app-root /private/tmp/faultline-apple-positive-v2/setup-v1/runtime --install-root /usr/local --disable-kernel-install --timeout 15
```

For every subprocess: cwd `/`, closed stdin and unrelated descriptors, exactly
`HOME=/Users/grove`, `PATH=/usr/bin:/bin`, `LC_ALL=C`, plus:

```text
XDG_CONFIG_HOME=/private/tmp/faultline-apple-positive-v2/setup-v1/config-home
CONTAINER_APP_ROOT=/private/tmp/faultline-apple-positive-v2/setup-v1/runtime
CONTAINER_INSTALL_ROOT=/usr/local
```

The private XDG source prevents startup from copying the real user's config;
the pinned app-root config takes precedence over installation defaults.
[ConfigurationLoader](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPersistence/ConfigurationLoader.swift)
and [PathUtils](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerPersistence/PathUtils.swift)
define that behavior. The existing client/API executable paths resolve under
`/usr/local/bin`; no install, upgrade or new executable is requested.
Offline inspection found five shipped plugin directories and no custom-plugin
directory. The helper pins their observed public config hashes and refuses new
or changed plugin metadata before service contact. Those hashes identify current
configuration, not signatures or independent binary provenance. The API reads
the copied app-root config; it does not repeat the user's config-copy step.

## Effects, budgets and observations

- **Persistent effects:** current-user launchd API/machine/image and other required
  Container helper registrations, runtime plists/state and public init content.
  Source config: `setup-v1/config-home/container/config.toml`; copied read-only
  config: `setup-v1/runtime/config/config.toml`; API plist:
  `setup-v1/runtime/apiserver/apiserver.plist`. Other runtime state/content/snapshots
  stays under that runtime root. Normal macOS unified logs may also be written.
  Leave the root intact while services are registered; stop does not delete evidence.
- **Network/download permission:** host DNS/TLS/HTTPS to ghcr.io and its registry
  blob/CDN redirects for **only the pinned init and its referenced OCI content**.
  Startup can download init despite `--disable-kernel-install`, as shown in
  [SystemStart](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStart.swift).
  No worker image, kernel archive, builder, Python package, registry login or
  supplied credentials. Normal runtime registry authentication lookup may occur;
  do not supply/extract secrets or answer a login prompt. Init payload bytes have
  not yet been independently verified; metadata existence alone will not verify them.
  Startup also creates the built-in default NAT network and loopback DNS listeners
  at `127.0.0.1:1053` and `127.0.0.1:2053`, according to the pinned
  [API startup source](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/APIServer/APIServer%2BStart.swift).
  Include these host network/helper effects in this approval; they are not a
  guest network attachment. No manual system DNS configuration is changed.
  Do not answer an administrator/security prompt; stop and retain the failure.
- **Resources:** zero VM/workload allocation authorized; one setup CLI at a time.
  Preflight launchctl calls: 5 s each; startup: 120 s outer timeout (its `--timeout 15`
  covers only API readiness); post-start status and init inspection: 15 s each;
  final labels: 5 s. Failure recovery gets 35 s plus a 5 s label check. Maximum
  summed subprocess waits: 205 s, excluding local filesystem/scheduling delays.
  Retain at most 64 KiB per command stream; capture assumes finite trusted CLI
  output, not a live output quota. Host service CPU/RAM/disk usage has **no hard
  quota supplied by this CLI**; approval must accept that setup risk. Matching
  init configuration gives the source-defined 512-MiB sparse snapshot capacity,
  not a total host-storage quota. No new VM resource budget is approved here.
- **New host evidence:** exclusively create `evidence/setup-v1.json`. Record exact
  source hashes, argv/environment, return codes/output, elapsed time and recovery.
  Post-start status must report running, the dedicated root, install root
  `/usr/local`, server 1.5.0 and commit prefix `d265d66`. Check copied config bytes
  and nonempty `image inspect` output for the exact init reference. Record filtered
  Container launchd labels. This is setup evidence, not complete blob/snapshot
  verification, VM-lifetime evidence or qualification.

## Failure and recovery

Nonzero exit, timeout, wrong session/root/version/config, missing init metadata,
oversized retained output or any exception stops the sequence. Startup can log an
init-pull error yet return zero; the separate exact-init inspection is required.
If startup was attempted after the empty-namespace guard, the helper runs:

```text
/usr/local/bin/container system stop --prefix com.apple.container.
/bin/launchctl list
```

This broad stop is authorized **only for this initially empty, exclusively owned
setup session**, which requests no containers. It is not the later synthetic-VM
cleanup policy. Apple's [SystemStop](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/SystemStop.swift)
operates across that prefix; never use it against pre-existing or concurrent work.
Record remaining labels: zero stop exit is insufficient. Remaining labels or a
failed recovery mean **stop and review**, no retry/force kill/pruning/deletion.
Removing launchd labels is not independent proof of host vmnet/DNS teardown;
uncertain residual network/helper state requires scoped recovery review.
If the coordinator is killed, services may persist. In the same exclusive session,
the operator may run the exact stop command with the environment above, then check
labels; if another user/command has intervened, request identity-scoped recovery
instead. No claim of automatic coordinator-death containment is made for setup.

On success, services remain registered for the next separately reviewed stage.
Do not run this helper again. Review the receipt, verify artifact bytes and obtain
separate worker/kernel provisioning authority. Synthetic positive execution still
requires its separate resource/guardian/observation approval; negative controls
remain separate again. Keep PR #17 draft, issue #2 open, the skill advice-only and
experiment #10 **NOT RUN**.
