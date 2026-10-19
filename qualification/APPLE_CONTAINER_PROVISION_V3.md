# Provision-v3: verify and copy the existing ARM64 Linux Image

**PREPARED, NOT EXECUTED. Separate execution authorization required.** PR #17
remains draft, issue #2 open, and Faultline execution **NO_GO / UNAVAILABLE**.
Provision-v1/v2 are consumed. Their files, permissions and receipts are untouched.

Provision-v2 copied the archive member but failed the subsequent ELF check.
Its original failure receipt is
`/private/tmp/faultline-apple-positive-v2/evidence/provision-v2.json`, SHA-256
`c56a7cdf32130e60142adc66ecb43bfa034191ec867dad43cf3682dab17727c6`.
The original v1 receipt retains SHA-256
`ad1949e4a3fb2dbc70ebcb5a34bf12b0a40a2581ac7fb667c85e5383707259e2`.
The existing v2 file is preserved at
`/private/tmp/faultline-apple-positive-v2/provision-v2/vmlinux-6.18.35-197-debug`:

| Observation | Value |
| --- | --- |
| File bytes | 30,423,552 |
| SHA-256 | `fb2cfb79eb1ae19447a85d75682d7fa5cfec97e24beb2609a492b806e8072c8d` |
| First 16 bytes | `4d5a40fa196058140000000000000000` |
| ARM64 Image magic at offset 56 | `41524d64` (`ARMd`) |
| Effective image size | 31,129,600 |
| Flags / page size | `0xa` / 4096 bytes |
| Text offset / PE-header offset | 0 / 64 |

The [Linux ARM64 boot specification](https://docs.kernel.org/arch/arm64/booting.html)
defines this raw Image format. The new parser requires the 64-byte header and magic,
decodes its fields little-endian, rejects big-endian kernels and reserved flag bits,
and checks the three reserved 64-bit fields are zero. It permits the PE-header
offset, checking its alignment and bounds. Defined page-size and placement flags
are decoded. Scoped admission requires a nonzero effective size covering the file,
both bounded by 128 MiB, and a 4-KiB-aligned text offset no greater than 128 MiB.
**Effective image size may exceed file length; equality is not required.** ELF is
rejected as the kernel format here; the worker interpreter keeps its separate ELF
checks. This parser is scoped to this modern pinned kernel, not a general bootloader.

Header validation alone never establishes provenance. Preparation independently
rehashed the **696,573,576-byte** existing Kata archive, SHA-256
`8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5`,
and compared the existing kernel **byte-for-byte** against its exact regular member
`opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug`. The comparison passed
without writing or extracting a file. Worker content/interpreter/sparse-snapshot
verification still matches both original receipts. See the
[preparation review and source pins](2026-10-19-apple-container-provision-v3-review.json).

The exact command for a later, separate execution approval, from
`/Users/grove/projects/faultline`, is:

```sh
/usr/bin/env -i HOME=/Users/grove PATH=/usr/bin:/bin LC_ALL=C TZ=Europe/Oslo /opt/homebrew/bin/python3 -I -B -c '
import hashlib
from pathlib import Path
path = Path("/Users/grove/projects/faultline/qualification/apple_container_provision_v3.py")
source = path.read_bytes()
if hashlib.sha256(source).hexdigest() != "f714443cb19964f9f4117edd0834ba3971f3aadce300d136f5d394c87ac792d7":
    raise SystemExit("provision-v3 source hash mismatch")
exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})
' provision-v3
```

The wrapper executes the exact bytes it hashes. The helper imports only the frozen
v1 helper, hash-pinned to
`2da6578d3c1cb49798ccc0f82db8f6e54c357c4a5c671736dfe556e2104dd67c`,
for content/snapshot/archive-reading primitives; its entrypoint is never called.
The consumed v1/v2 helpers, procedures and manifests are unchanged.

The continuation exclusively creates
`/private/tmp/faultline-apple-positive-v2/evidence/provision-v3.json` and a fresh
mode-0700 `/private/tmp/faultline-apple-positive-v2/provision-v3`. An existing receipt
or destination refuses reuse. It checks pinned v1/v2/setup receipts, runtime state/
config, original default-kernel-store identity and worker/snapshot identities.
It rehashes the v2 file and archive, validates the raw header and scans the archive
with the existing 8-GiB decompressed-read and 100,000-header bounds. A missing,
duplicate, nonregular, wrong-size or changed member stops the attempt.

After successful comparison and storage admission, copy only the existing v2 file
to this exclusive new destination, with reads bounded by its pinned length:

```text
/private/tmp/faultline-apple-positive-v2/provision-v3/vmlinux-6.18.35-197-debug
```

Fsync and verify the new file's exact size/hash/header before making it **0444**.
Reverify original receipts/runtime/worker/v2 file and the archive-member comparison
before success. Make the successful v3 directory **0500**; the new receipt is fsynced
and made **0444** on success or handled failure. Preserve any partial new copy and
failure receipt; do not clean up, retry, change old permissions or repair services.
Abrupt coordinator death can leave incomplete new state; preserve and review it.

Storage admission counts the **entire preparation bundle**, including all previous
setup/provision roots, inputs, original fixtures and evidence. Limits stay
**515 GiB logical, 8 GiB allocated and at least 16 GiB free**. Check before
verification, before copying and after copying; reserve 128 MiB for the prospective
kernel and 1 MiB for receipt growth inside the same caps. Retain 8192-entry/depth-16,
link/special-file rejection and the 600-second alarm. These are phase checks, not
hard live quotas. Keep other Container management idle during the operation.

There are **no network, pull, service or VM subprocess calls**. No retrieval,
default-kernel/config mutation, shutdown/restart, cleanup, guardian installation,
VM/canary, guest Python or Faultline challenge is authorized. Publication of this
candidate does not authorize execution, merge, issue closure or qualification.

Validation: **68 scoped tests pass**, including seven v3 regression tests with
synthetic raw Images/archives, malformed/endian/reserved/size cases, ELF rejection,
changed content, duplicate/nonregular/missing/truncated members, exclusive output,
partial copies, read-only final permissions, all-root storage limits, preserved
identities and failed final admission. Real-archive preparation only read/compared
bytes; provision-v3, guardian installation and VM execution were not run.
