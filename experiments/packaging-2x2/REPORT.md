# Packaging visibility/instruction comparison — 2026-10-20

Four fresh, read-only audits completed, one per frozen 2×2 cell. **None surfaced
the targeted exclusive-prerelease-bound/default-policy interaction**, either as
a suspected bug or as a contract conflict. Both specification-present auditors
retrieved the relevant historical PEP text. These observations do not demonstrate
a detection improvement or isolate attention, interpretation, or prioritization.

| Cell | Instructions | Historical specification | Target detection/conflict | Accepted graded units | Unresolved units | Unsupported claims | Identified false-positive claims |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| [A](audits/A/response.md) / [grade](grades/A/response.md) | Old | Absent | Miss | 3 | 0 | 0 | 0 |
| [B](audits/B/response.md) / [grade](grades/B/response.md) | Old | Present | Miss | 2 | 1 | 2 | 0 |
| [C](audits/C/response.md) / [grade](grades/C/response.md) | New | Absent | Miss | 3* | 0 | 0 | 0 |
| [D](audits/D/response.md) / [grade](grades/D/response.md) | New | Present | Miss | 1 | 1 | 2 | 0 |

There are 10 numbered findings. C's grader additionally counted its substantive
contract-resolution caveat as a third unit (*), giving 11 graded units and 21
separately graded claims. All raw accounting is preserved: nine accepted units,
two unresolved, four unsupported claims, and zero identified false-positive,
duplicate, or out-of-scope units. These are repeated observations on one source
case, not nine distinct bugs or a precision estimate. Unsupported requirements
were retained as unresolved rather than silently counted as false positives.
[Machine-readable results](results.json) bind each count to its raw grade.

## Contract ambiguity and recommendation

The specification-absent new-instruction report explicitly says that a separate
nonempty-set fallback policy needs resolution before prescribing an outcome.
Its independent grader accepts that as an appropriately handled contract
question. This concerns a different behavior from the targeted historical gap.

Both specification-present reports suggest unconditional True/False assertions
for installed prereleases under exact equality and exclusion. Their independent
graders agree that base-version normalization and missing coverage are visible,
but the packet does not establish the special `installed=True` policy. Ordinary
equality/exclusion semantics do not settle that lifecycle contract. B acknowledges
the uncertainty but still prescribes unconditional outcomes; D calls the concern
high-confidence despite the undocumented parameter. Both remain unresolved.
Thus the new guidance was not consistently followed, and this matched pair does
not show improved handling of that ambiguity. C's appropriate caveat and A's
qualification of another concern also do not establish an instruction effect.

**Retain the PR #21 guidance provisionally, unchanged.** It states the desired
conditional-assertion standard clearly, but this comparison does not validate
better detection or reliable compliance. No revision or reversion follows this
single case. The canonical skill was not edited. No execution capability is
enabled, and both PRs remain unmerged.

## Fixed inputs and independent grading

The [protocol](protocol.json), [rubric](grading-rubric.md), ordinary
[audit prompt](audit-prompt.txt), and [grading prompt](grade-prompt.txt) were frozen
before the first audit. Old instructions are the exact PR #20 bytes; new
instructions are the exact PR #21 bytes at
`0c21de7f8723494e78cfcd194e8962209953174d`. Both release-boundary and verification
sections are byte-identical. There was one first response per cell, no retries,
no additional target cases, and no changes in response to an outcome.

All cells used the original 43 packaging files at
`a716c52b5f3ca9b4a512f538b80ced8ee01b2775`, verified against the pilot's
[source hashes](source-manifest.json). Source, tests, ordinary request, requested
model (`gpt-6.1-sol`), effort (`xhigh`), CLI (`0.163.0`), sandbox settings, and
grading criteria were fixed. Only the assigned instruction bytes and addition
of the historical PEP document varied. The full document, rather than a selected
answer-bearing excerpt, came from official python/peps commit
`d55eeb1958a4698b7f1fd482d424be869634f1a6`, before the packaging snapshot;
[acquisition metadata](specification/acquisition.json) records its identity.

[Visibility inventory](visibility-inventory.json) records withheld root
configuration and absent transitive references. Root configuration stayed absent
in every cell to preserve the original packet. Auditors received no oracle,
expected assertion, fix history, previous reports, rubric, or treatment labels.
Their source directories contained no Git repository. The shared filesystem was
restricted by instructions and observed reads, not an OS read-access barrier.

Four further fresh sessions independently graded one report each against its
supplied packet using the same model, effort, prompt, and rubric. Graders did not
conduct the audits and did not see the instruction version or treatment label.
The rubric revealed the target interaction to graders, with an explicit duty to
challenge the historical expectation. It did not require a positive assertion
when the supplied policy was unsettled. All grades are source-only model
judgments, not human adjudication or reproduced bugs.

The rubric counts detection or an explicitly surfaced contract conflict. It
splits materially distinct claims and conservatively retains unsupported policy
claims as unresolved; an established false positive requires contradictory or
already-protecting evidence. A correct current implementation can still have a
valid protection gap. Raw reports and grades, including uncertainty, are retained.

## Evidence, execution fence, and limits

[Read bindings](read-visibility.json) locate the autodetection guard, forced-policy
shared assertions, existing False expectations, and comparator exception in every
audit's captured stdout. They also locate the normative passage in both
specification-present audits. Captured retrieval does not prove attention or
complete host/model context delivery. The reports' omission therefore remains
an output-level observation, with its internal cause unresolved.

The [collector](run.py) retained complete raw stdout, stderr, receive-time event
ledgers, prompts, final responses, timings, and packet hashes under [audits](audits)
and [grades](grades). [Grade scheduling](grade_when_ready.py) overlapped a completed
packet's grader with later audits to avoid waiting unnecessarily. Audits themselves
were sequential in predeclared order A, B, C, D. Elapsed values are descriptive
records only, with queue, host load, and generation mixed together; this was no
latency A/B. Model-request settings are known; actual server model identity was
not independently exposed by these events.

[Offline verification](verify.py) passes for all four audits and all four grades:
frozen prompts/collector/rubric, complete raw event streams and final responses,
identical source/test packets, correct per-cell factors, blinded grading inputs,
and consistent claim/whole-finding accounting. The collector also asserted that
each staged packet was unchanged after its session. [Tool review](tool-review.json)
retains every observed command and records file readers/search only, with no
observed history access, external retrieval, Docker, or target execution. This is
event inspection, not kernel telemetry or sandbox qualification.

[Preservation evidence](preservation.json) verifies all 103 original local files,
their Git status and HEAD, and all 115 previously tracked PR #21 files preserved
(one additive README paragraph; all other bytes unchanged).
This includes pilot evidence, prior diagnostics, security/qualification history,
and the canonical skill. Docker remains disabled and execution remains
**NO_GO / UNAVAILABLE**. No unrelated evaluations, graders, qualification, or
standalone validator were rerun; no dependencies were installed. The previously
reported missing-`yaml` validator limitation remains untested here.

One run per cell on one known public historical Python case provides no
reliability estimate, statistical effect, or causal attribution to instructions
or visibility. There is no fresh protected control or false-positive denominator;
zero identified false positives cannot establish a false-alarm rate. Public
history may be familiar from training. Finding selection and grader interpretation
can vary between fresh sessions, and order, concurrency, and server state remain
potential confounders. Ordinary whole-repository usability, human comprehension,
repeatability, and the original Click/Requests ambiguity cases were not evaluated.
No faster responses or broader quality gain is claimed.

## Reproduction without target execution

Acquire the exact public packaging commit as a bare repository with hooks disabled.
Read the 43 manifest paths with `git show` or an archive reader as data; verify all
hashes. Stage them under a temporary `stage/project` directory, with no `.git` or
repository instructions. Keep root configuration withheld. Use the archived PEP
and instruction files exactly. Place this experiment under
`<temporary>/repo/experiments/packaging-2x2`; the collector derives
`<temporary>/stage` and `<temporary>/grading` from that layout. The archived prompts
contain the original absolute temporary path: update both path prefixes and their
protocol digests together for a separate reproduction, and freeze that new identity
before launching. Preserve the original archive.

On a separate copy without existing output directories, run `python3 -B run.py
audit` and `python3 -B grade_when_ready.py` through the existing authorized model
host. Those are evaluator scripts, never packaging code. Retain every first result;
future outputs can differ. No dependency installation is needed. To inspect only
this completed archive, run `python3 -B experiments/packaging-2x2/verify.py` from
the Faultline checkout; this makes no model calls and executes no target code.
