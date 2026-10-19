# Next request: Python worker and dedicated Kata kernel only

**PREPARED, NOT EXECUTED. Separate approval required.** PR #17 remains draft,
issue #2 open and execution **NO_GO / UNAVAILABLE**. This request provisions two
artifacts using the already running setup-v4 services. It grants no VM, canary,
guardian installation, #10 or executable Faultline skill authority.

## Accepted setup-v4 result — do not repeat

The operator's [unaltered receipt](2026-10-19-apple-container-setup-v4.json) matches
the original `/private/tmp/faultline-apple-positive-v2/evidence/setup-v4.json`,
SHA-256 `7366b677973d26db9b16efbfc1cae563e262de59d4fb1d695ed79d56f73b584c`.
Operator exit 0; result `SERVICES_STARTED_INIT_CONTENT_SNAPSHOT_CHECKED`;
`qualification_granted: false`; zero VM/canary launches. Four service identities
were checked and left running, without failure recovery. Source/config/observer
hashes match the published candidate. This is operator-supplied execution evidence,
independently hash-compared here, not a run witnessed or repeated by Codex.
See the [provenance review](2026-10-19-apple-container-setup-v4-outcome.json).

Accept the pinned Containerization 0.47.0 init as provisioned for this exact host/
runtime configuration. Its 69,253,615-byte layer, other OCI blobs and 640-MiB sparse
snapshot passed the recorded checks. No init download, setup repetition, signature/
hardware prerequisite rerun, service restart or recovery is requested. All setup
attempt identities, including setup-v4, are consumed. Historical authorization
documents/review hashes remain frozen in Git history; they are not current requests.

## One exact authorization

From `/Users/grove/projects/faultline`, approve one operator-Terminal execution:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B qualification/apple_container_provision.py provision-v1
```

Use the exact source hashes in the [preparation manifest](2026-10-19-apple-container-provision-v1-review.json).
It also pins the unchanged setup-v4 helper/observer used only as pure identity/parser
functions; their entrypoints are never called. No package installation is required:
the installed host Python has standard-library zstd support, exercised with synthetic
archive unit tests. Do not execute any downloaded ELF on the host.

Exclusively create `/private/tmp/faultline-apple-positive-v2/evidence/provision-v1.json`
and a fresh mode-0700 `/private/tmp/faultline-apple-positive-v2/provision-v1`.
Existing receipt/directory refuses reuse before service contact. All subprocesses
have cwd `/`, closed stdin/unrelated descriptors, and exactly:

```text
HOME=/Users/grove
PATH=/usr/bin:/bin
LC_ALL=C
TZ=Europe/Oslo
XDG_CONFIG_HOME=/private/tmp/faultline-apple-positive-v2/setup-v4/config-home
CONTAINER_APP_ROOT=/private/tmp/faultline-apple-positive-v2/setup-v4/runtime
CONTAINER_INSTALL_ROOT=/usr/local
```

First verify the accepted receipt hash, pinned existing executable bytes and unchanged
runtime config. Read only the four exact setup-v4 launchd targets and targeted
PID/UID/executable/birth records; refuse changed roots/identities. Raw launchd dumps
are discarded. Then `container system status --format json` must report running
1.5.0/full commit, the setup-v4 app/install roots and zero existing containers.
These are guards on use of the current services, not a repeat of completed setup
or prerequisites. Keep other Container management idle for this one operation.

The only worker retrieval command is:

```text
/usr/local/bin/container image pull --platform linux/arm64/v8 --scheme https --progress plain --max-concurrent-downloads 1 docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d
```

It uses already registered services, and explicitly retrieves/unpacks the worker.
No `system start` or init pull occurs. Require one new worker reference alongside
the unchanged init entry. Verify the local generated index/platform, exact worker
manifest, config `sha256:da841a7026abc0089180121604f6d0ba4324998e2d133eccae13f22707055dc1`
and all four layer digests/sizes from the frozen [worker review](2026-10-18-apple-container-positive-review.json):

| Layer SHA-256 | Compressed bytes |
| --- | ---: |
| `c75f989a229d12b2d2613a5997de9ff3546f664c22da9248720033a2410220f6` | 28,137,179 |
| `aa08835651e777794bde3e8c99bee012c418f60d0d164df22497fa01dc72aca5` | 3,176,232 |
| `7b2df2902dddd1a4510670c4d3a6d61b4458fa3e7c1ae0b262d75bde1349ab14` | 14,748,696 |
| `32020fed7f2a057b9cee7fdbfa3ea9fc394149118d7a951c462c7055c3cd3f56` | 250 |

Require linux/arm64(/v8), regular singly linked blobs, exact byte lengths/SHA-256
and empty ingests. Read layer archives offline, without extracting a host tree:
verify `/usr/local/bin/python3 -> python3.13` and the executable AArch64 ELF
`/usr/local/bin/python3.13`, recording its size/hash. Relevant interpreter whiteouts
or unexpected link/file forms stop the attempt. No guest interpreter is invoked.
Check snapshot-info, EXT4 geometry and a canonical hash of its data extents plus
hole map/logical length. This avoids reading 512 GiB of sparse zeros. Unsupported
hole observation, too many extents or more than 8 GiB data to read stops, without
fallback. These are fresh-unpack/content/structural checks, not full fsck or a
file-by-file independent reconstruction of the snapshot.

Then download exactly this archive into the fresh provision-v1 directory:

```text
/usr/bin/curl -q --fail --silent --show-error --location --proto =https --proto-redir =https --max-redirs 5 --connect-timeout 10 --max-time 300 --max-filesize 696573576 --output /private/tmp/faultline-apple-positive-v2/provision-v1/kata-static-3.32.0-arm64.tar.zst https://github.com/kata-containers/kata-containers/releases/download/3.32.0/kata-static-3.32.0-arm64.tar.zst
```

The public release metadata reports **696,573,576 bytes** and archive SHA-256
`8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5`, matching
Container 1.5.0's pin. Verify both before decompression. The host helper scans the
archive using standard-library zstd/tar readers and copies **only** the one regular
member `opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug`, capped at 128 MiB,
to the new dedicated path:

```text
/private/tmp/faultline-apple-positive-v2/provision-v1/vmlinux-6.18.35-197-debug
```

Reject a missing/duplicate/nonregular member, wrong archive hash/size, oversized
member or non-AArch64 ELF. Record the extracted SHA-256/size and archive/member
provenance, chmod the new kernel 0444, and retain the archive. Its extracted hash
will become an exact input to the later positive-stage request; it is not invented
before retrieval. No generic tar extraction, scripts or package hooks run.

**Never call `container system kernel set`.** The pinned
[KernelSet](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/System/Kernel/KernelSet.swift)
updates the default. The pinned
[custom-kernel path](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/ContainerCommands/Utility.swift)
accepts an existing file through `--kernel`, avoiding that mutation. The proposed
operation does not create/modify `runtime/kernels`, default aliases, private TOML
or unrelated Container state. Recheck current service/process identities and
unchanged config and original empty kernel-store identity/default-kernel absence before recording
`WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM`.

## Host/network/storage/time scope

Allow host DNS/TLS/HTTPS to `registry-1.docker.io`, public `auth.docker.io` and registry
blob/CDN redirects only for the pinned worker graph; and `github.com` plus release
asset/CDN redirects only for the exact Kata archive. HTTPS redirects only. No manual
login, supplied/extracted credentials, answered security/admin prompt, proxy/TLS
configuration change, GHCR re-download or diagnostic probe. Normal existing registry
credential lookup can occur inside the Apple image service. Curl disables its user
configuration with its first `-q` flag and receives no authentication options.

Writes: worker content/reference/ingest/snapshot state under the setup-v4 runtime,
the new provision-v1 archive/kernel and receipt, plus ordinary service/OS logs.
No new service registration, listener/NAT configuration, host mount or default
kernel mutation. Existing services remain registered/running on success or failure.

**Actual baseline:** setup-v4 uses **740,351,288 logical / 273,485,824 allocated bytes**,
both in its receipt and the separate read-only filesystem count at preparation time.
The 640-MiB init snapshot alone has 189,022,208 allocated bytes.
The pinned [SnapshotStore](https://github.com/apple/container/blob/d265d669ecae041bf338cb3b39c4118316d138f0/Sources/Services/ContainerImagesService/Server/SnapshotStore.swift)
requests a **512-GiB sparse minimum** for non-init images, plus journal overhead.
Both ImagePull and ImageLoad unpack; neither exposes a no-unpack/capacity flag.
Use this shipped path for one image rather than introducing a custom image importer
or changing the live init configuration. A sparse logical length is not physical
disk allocation or a VM memory allocation.

Admission/phase limits over **setup-v4 plus provision-v1 together**:

- At least **16 GiB free**, at most **8 GiB allocated** and **514 GiB logical**.
  Includes existing init, worker blobs/sparse snapshot, 696,573,576-byte archive and
  at most 128-MiB extracted kernel. Check before worker pull, after pull, after
  archive download and after extraction. Worker snapshot alone is capped at 513 GiB.
- At most 8192 filesystem entries, depth 16; no links/special files. Metadata files
  at most 1 MiB. Each worker layer at most 32 MiB compressed; at most 40,000 headers
  and 512 MiB decompressed reads per pinned layer. Kernel archive scan at most
  100,000 headers / 8 GiB decompressed reads. No other archive members are written.
- One CLI/download at a time; worker pull timeout **180 s**, curl **300 s** with
  **310-s** subprocess timeout, status **15 s**, observations **5 s** each. The
  standalone trusted coordinator has a **600-s host alarm** covering phases/hashing.
  At most 64 KiB per ordinary retained stdout/stderr stream; launchd stdout parses
  at most 4 MiB and is discarded. Capture bounds are checked after trusted CLI output.

These are **phase admission checks, not hard live service CPU/RAM/disk/network-byte
quotas**. A timed-out image client may leave its in-flight service operation running;
the coordinator alarm cannot terminate that daemon. No automatic larger budget,
download retry, cache pruning or service stop is granted. Accept this provisioning-
only residual exposure explicitly. Zero VMs/workloads or VM-budget increase.

## Failure and next stage

The new receipt records exact argv/environment, source hashes, status/partial
timeout output, phases, local hashes and errors, fsyncing at command boundaries.
Any changed service/receipt/config, timeout, nonzero command, size/digest mismatch,
partial ingest, unsupported sparse observation or admission failure means **FAILED**.
Preserve the old receipt, all artifacts/partial files, current four services and
runtime state. Do not reset/retry, remove an image, boot out a service or reclaim disk.
Review the recorded failure; any scoped shutdown/cleanup needs separate approval.
Coordinator death can leave a partial new receipt and in-flight image work; preserve
both and review before any further effect. No later stage starts automatically.

The [minimal future guardian](apple_container_guardian.py) and
[future-stage procedure](APPLE_CONTAINER_GUARDIAN.md) are prepared/tested only.
They are not installed or invoked by this provisioning command. A later positive
authorization must consume the successful provisioning receipt, pin the resulting
kernel/interpreter/snapshot identities, seal the exact create/configuration/guardian
plan, and explicitly authorize one frozen synthetic Python run plus its termination
actions. No #10, negative controls or general qualification follows from that run.

Validation: **59 scoped tests pass**, all service/download/VM operations mocked;
synthetic archive/sparse-file checks exercise the readers. The original 49 setup/
recovery tests remain included. Full native-lifetime tests are not run.
