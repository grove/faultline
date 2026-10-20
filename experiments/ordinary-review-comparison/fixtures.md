# RO-1 case preparation

**SIX CANDIDATES PREPARED — STUDY NOT FROZEN — NO AUDITS RUN (2026-10-20).**
These are source-only curation hypotheses, not independently validated findings.
The user (`grove`) is sole human curator and grader by explicit instruction.
The preparation assistant does not conduct either audit arm or supply grades.
Worker-independent judgment remains pending; curation/grading independence is
unavailable. Follow [PROTOCOL.md](PROTOCOL.md).

## Selection and provenance

The preparation pool/order was recorded before detailed inspection: cachetools,
blinker, more-itertools, MarkupSafe, dateutil, validators, boltons, exceptiongroup.
An earlier `itsdangerous` serializer read is disclosed and that project excluded.
This is convenience sampling, not a random or representative sample; public
training exposure is unknown. None of these six behaviors appears in the prior
Faultline cases. No audit/pilot output was used to select them.

| Pool order | Repository | Disposition after source inspection |
| --- | --- | --- |
| 1 | `tkem/cachetools` | c03: existing TTL expiry assertions; suitable protected behavior |
| 2 | `pallets/blinker` | UNAVAILABLE: the named remote returned repository not found; no silent URL substitution |
| 3 | `more-itertools/more-itertools` | c04: protected low-risk iterator-consumption scope |
| 4 | `pallets/markupsafe` | c05: equivalent native/C escaping and shared test parametrization |
| 5 | `dateutil/dateutil` | c02: leap-year test repeats non-leap dates in one direction; candidate protection gap |
| 6 | `python-validators/validators` | c06: documented IANA policy versus explicit `.onion` allowance |
| 7 | `mahmoud/boltons` | c01: AtomicSaver failure-path protection; fills remaining gap slot |
| 8 | `agronholm/exceptiongroup` | Not inspected; reserve not needed; remote identity alone queried |

On 2026-10-20, `git ls-remote` resolved public HEADs; task-local bare repositories
fetched those exact commits with hooks disabled. `git show <commit>:<path>` read
regular blobs into disposable source-data copies under
`/private/tmp/faultline-ro1-inspection/<repository-name>`; no checkout, imports,
tests or target helpers ran. The original remote repositories were not modified.

[source-manifest.json](source-manifest.json) reuses the existing real-repository
pilot's list of `case`, `repository`, `commit` and per-file `files` SHA-256 values.
It identifies **57 original files, 440,444 bytes**, including licenses and root
test configuration. Each extracted file was compared with its pinned Git blob.
The manifest SHA-256 is
`adfb1fc5170511d8c630a56a56ea460c253c7a4483d61009273854733ece4a95`.
Source is not duplicated in this repository; the immutable public commits plus
hashes are the durable fixtures, following the earlier pilot's approach. Missing
upstream content later means UNAVAILABLE, not permission to substitute revisions.

The packets contain whole selected files, not answer-bearing excerpts. Other
modules, dependency implementations, installed environments and runtime results
are absent. This bounds judgments to each named API; graders must not infer a
whole-repository test gap from an omitted file. Read root configuration as data.
Missing context can refute a hypothesis or leave it unresolved.

## Candidate cards — WITHHELD FROM AUDIT WORKERS

Give each worker only its manifest packet and the neutral scope below, plus B's
canonical skill. Do not give this file, category labels, answers, history, issue
links or counterpart reports. Final human curation may reject any candidate;
record rejection and refreeze before any model dispatch, never after outputs.

### c01 — AtomicSaver failure handling

Source: [boltons at 4e5faa3d](https://github.com/mahmoud/boltons/tree/4e5faa3d7e4008d89e0d8bf1ea87b6d9a061a16d).
Neutral scope: `AtomicSaver/atomic_save and their tests`.
Role: consequential protection-gap hypothesis; possible implementation defect.

`boltons/fileutils.py:335` documents preserving the destination on failure;
`:367` documents removing the part file on exception by default. `__exit__`
at `:466` flushes/fsyncs/closes before entering its exception cleanup branches.
`tests/test_fileutils.py:32` checks only successful path-like saving. A repository
source search found no other AtomicSaver test; the docstring example demonstrates
a body exception but does not assert cleanup or destination bytes.

Expected observation: suggest a failure-path test that starts with a known
destination and asserts its bytes remain unchanged, the original exception
propagates and default part-file cleanup occurs. A flush/fsync error can bypass
the visible cleanup; this is a source hypothesis, not a reproduced leak. Retaining
part files with `rm_part_on_exc=False` is a valid alternative and must be respected.
Use existing `tmp_path`/file tests; a controlled mocked I/O error is a proposed
test, never an instruction to inject faults during this evaluation. Refute by
locating equivalent assertions or a narrower supported cleanup contract.

### c02 — Leap-year datetime differences

Source: [dateutil at df91cdd2](https://github.com/dateutil/dateutil/tree/df91cdd2ed57785b157c0ca0641450d7423170a3).
Neutral scope: `relativedelta datetime differences across month ends and their tests`.
Role: correct-implementation/protection-gap hypothesis, not a claimed source bug.

`tests/test_relativedelta.py:53` names a leap-year test: its backward assertion
uses 2012, but `:58` repeats the 2003 forward assertion from the preceding
non-leap test. `src/dateutil/relativedelta.py:114` constructs a difference by
month adjustment followed by remainder; `:366` clamps to the selected month's
length. The class contract and `docs/relativedelta.rst` describe calendar-relative
differences and month-end behavior.

Expected observation: the named test does not independently protect its forward
leap-year scenario. Proposed assertion: difference from 2012-01-31 23:59:59 to
2012-03-01 00:00:00 equals one month plus one second; adding that difference back
reconstructs the endpoint. Calendar differences affect scheduling/date calculations.
The present algorithm appears consistent by inspection. Reject this hypothesis
if other tests already distinguish the relevant leap-year forward failure or
if the grader finds no consequential additional protection. Do not count a
cosmetic duplicate-test complaint as a meaningful gap or demand a particular
internal algorithm.

### c03 — TTL expiry control

Source: [cachetools at 6f23e2a7](https://github.com/tkem/cachetools/tree/6f23e2a7b75a42d30cb9d890ab3ca4059ee01bfd).
Neutral scope: `TTLCache expiry at the deadline and iteration, with its tests`.
Role: protected selected behavior.

`src/cachetools/__init__.py:477` and `:519` use strict-before-deadline membership
and iteration; `:544` removes expired entries. `docs/index.rst:112` documents TTL
and expiration. `tests/test_ttl.py` covers exact expiry, explicit `expire(time)`
return values and bare iteration skipping expired entries; `tests/__init__.py`
contains shared cache assertions. Expected: no invented missing-boundary finding
for these observations. Deletion versus lazy removal is permitted as documented;
do not demand immediate physical eviction from a read. This is not protection of
every TTL operation. Distinct, source-supported gaps remain gradable.

### c04 — Low-risk iterator consumption control

Source: [more-itertools at 4aeb4338](https://github.com/more-itertools/more-itertools/tree/4aeb4338ae1407d8da9723e86da99efeb446f719).
Neutral scope: `consume's documented iterator-advancement behavior and tests`.
Role: protected low-risk scope; no-finding is useful.

`more_itertools/recipes.py:163` documents advancement without returned values,
including exhaustion; it uses standard-library `deque`/`islice` at `:195`.
`tests/test_recipes.py:100` asserts partial, zero, negative and full consumption
through `next()` or an exception. The docstring also gives overshoot examples.
Expected: recognize existing observable assertions and a justified no-finding
for the declared cases. No demand to replace the efficient implementation with
a Python loop or to add tests for every standard-library property. Other
consequential gaps require their own contract evidence.

### c05 — Valid escaping implementations

Source: [MarkupSafe at 4e111271](https://github.com/pallets/markupsafe/tree/4e111271b1494995708a9e878a10829b5e10c7ba).
Neutral scope: `escape for ordinary strings and the Python/C implementations' tests`.
Role: valid alternatives; selected escaping observations protected.

`src/markupsafe/__init__.py:24` defines escaping of five characters.
`_native.py` uses replacement chaining; `_speedups.c` uses Unicode-width-specific
buffer scans. `tests/conftest.py:25` parametrizes the same assertions across
backends, skipping C when unavailable. `tests/test_escape.py:11` includes ASCII,
two-byte and four-byte strings, escaping at beginning/end, and empty input.
Expected: do not classify different algorithms or reusing the unchanged string
when no escaping is needed as defects. Do not claim the native backend lacks
tests just because the public import prefers C. A possible C skip is explicitly
allowed; no actual backend availability or passing tests were observed.

### c06 — TLD policy ambiguity

Source: [validators at 6ffd8625](https://github.com/python-validators/validators/tree/6ffd8625ee4272dade063653bff615014bdc4734).
Neutral scope: `domain's consider_tld policy and its validation tests`.
Role: conflicting contract evidence; uncertainty expected.

`src/validators/domain.py:58` describes restricting to IANA TLDs, while `:19`
adds `ONION` to its popular-TLD cache. The bundled `_tld.txt` has no `ONION`
entry; it identifies a 2024 snapshot, not current registry truth.
`tests/test_domain.py:49` explicitly expects `.onion` acceptance with
`consider_tld=True`. `utils.py` defines returned `ValidationError` semantics.

Expected: identify the mismatch or preserve uncertainty; do not prescribe
unconditional rejection as a verified fix. A maintainer must decide whether the
contract intentionally includes a special-use exception or the implementation
should be restricted. Conditional tests/docs changes may follow either policy.
An existing assertion is evidence of intent, not conclusive authority. No DNS,
network call, live-registry lookup or validation-code execution is needed.
