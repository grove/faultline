# Provision-v2: verify existing artifacts and extract one dedicated kernel

**PREPARED, NOT EXECUTED. Separate authorization required.** PR #17 stays draft,
issue #2 stays open, and Faultline execution remains **NO_GO / UNAVAILABLE**.
Provision-v1 exited 1 and its authorization is consumed. Do not repeat it.

The original receipt remains byte-for-byte unchanged at
`/private/tmp/faultline-apple-positive-v2/evidence/provision-v1.json`, SHA-256
`ad1949e4a3fb2dbc70ebcb5a34bf12b0a40a2581ac7fb667c85e5383707259e2`.
Its existing-service checks, pinned worker pull/verification and archive curl
completed successfully. Post-download storage admission failed before archive
verification or kernel extraction. No shutdown, VM or canary was authorized.
The v1 helper, proposal, preparation manifest, receipt and archive remain unchanged;
their hashes are recorded in the [v2 preparation review](2026-10-19-apple-container-provision-v2-review.json).

Read-only preparation independently verified the existing archive's exact
**696,573,576 bytes** and SHA-256
`8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5`.
The existing worker graph, all pinned blobs/platform/interpreter checks and full
sparse-snapshot verification match the v1 receipt exactly. Interpreter SHA-256:
`cb4548d280f38c2b1df4cba45f12c90a034729e08fce5bf1a223c58add0e21e3`.
Snapshot length: **550,829,555,712 bytes**; 4098 extents, **1,333,428,224 bytes**
read; extent-map/data SHA-256:
`af7e906cc24b34138962ebd6f000f68fbb9a7194d530a149c0fca87d4b6507f4`.
This is content/structure evidence, not fsck, guest execution or isolation proof.

The corrected combined budget is based on these observations:

| Component | Logical bytes |
| --- | ---: |
| Accepted setup before worker | 740,351,288 |
| Observed worker growth, including sparse snapshot | 550,875,626,653 |
| Existing archive | 696,573,576 |
| Maximum extracted kernel | 134,217,728 |
| Projected maximum total | 552,446,769,245 |
| 515 GiB limit | 552,977,039,360 |
| Remaining headroom | 530,270,115 |

The old 514-GiB limit left only 287,319,595 bytes after the worker. Current combined
allocated storage is **2,345,254,912 bytes**. Retain the **8-GiB allocated** ceiling,
**16-GiB minimum free**, 8192-entry/depth-16 limits, link/special-file rejection,
600-second coordinator alarm, 8-GiB decompressed archive scan, 100,000 headers and
128-MiB regular kernel-member maximum. Count **setup-v4 + provision-v1 + provision-v2**
together before/after extraction. Reserve the full maximum kernel size against
logical, allocated and free-space admission before extraction. These are phase
checks, not hard live quotas; concurrent external writes can change storage.

From `/Users/grove/projects/faultline`, the **one exact command for separate approval** is:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B -c '
import hashlib
from pathlib import Path
path = Path("/Users/grove/projects/faultline/qualification/apple_container_provision_v2.py")
source = path.read_bytes()
if hashlib.sha256(source).hexdigest() != "b14ae16b36e3f2dd198eac4558384711a60e00103668db9741e417511d7c8d8c":
    raise SystemExit("provision-v2 source hash mismatch")
exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})
' provision-v2
```

The wrapper executes the exact bytes it hashes. The continuation also pins its
unchanged v1 verification/extraction helper to SHA-256
`2da6578d3c1cb49798ccc0f82db8f6e54c357c4a5c671736dfe556e2104dd67c`.
It imports that helper's functions only; it never calls the consumed v1 entrypoint.
No dependency installation is needed.

Exclusively create the new receipt
`/private/tmp/faultline-apple-positive-v2/evidence/provision-v2.json` and fresh
mode-0700 directory `/private/tmp/faultline-apple-positive-v2/provision-v2`.
Either identity's prior use stops the attempt. Verify the original v1 and setup-v4
receipt hashes, pinned runtime config/state and original empty default-kernel-store
identity. Reverify the existing archive and worker/snapshot against the v1 receipt.
After storage admission, scan the existing archive and copy only the regular member
`opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug` to:

```text
/private/tmp/faultline-apple-positive-v2/provision-v2/vmlinux-6.18.35-197-debug
```

Use exclusive file creation. Reject missing/duplicate/nonregular/oversized members
and non-AArch64 ELF output; fsync, chmod 0444 and record its exact hash/size and
archive/member provenance. The extracted hash is unknown until authorized
extraction. Recheck storage, original receipt, archive, worker/snapshot,
runtime state/config and default-kernel-store identity before success. Checkpoint
the new receipt after verification/extraction phases; failures preserve partial
evidence and output without cleanup or retry. No later stage starts automatically.

**There are no subprocess, service, retrieval, guardian or VM calls.** Keep other
Container management idle during this command. Current service health is not
re-probed; existing services remain untouched. No image pull, curl, init retrieval,
service registration/shutdown/restart, cleanup, default-kernel/config mutation,
guardian installation, VM/canary, downloaded-code execution or guest Python is
authorized. Only the new receipt/dedicated kernel destination is written. This
request grants no publication, merge, issue closure or Faultline enablement.

Validation: **61 scoped tests pass**. Continuation fixtures cover reuse, mismatched
receipt/archive/worker/state, logical/physical/free-space admission, partial
extraction, concurrent state drift and consumed receipt/destination. Live calls
are forbidden by mocks; the shared extractor is exercised with synthetic archives.
No live continuation, real archive decompression/extraction or VM test was run.
