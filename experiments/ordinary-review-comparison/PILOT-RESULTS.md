# Two-case read-only pilot — 2026-10-21

**RUN: 4/4 first attempts completed. Provisional outcome: NO CLEAR BENEFIT.**
Faultline reported no weakness absent from ordinary review. This compares the
reports, not accepted findings: **human assessment by `grove` is PENDING**.
No suspected bug is counted as confirmed. Suggested tests are **NOT RUN**.

This pilot was explicitly authorized separately from the prepared six-case
[RO-1 study](PROTOCOL.md) in [draft PR #26](https://github.com/grove/faultline/pull/26).
Its token/cost enforcement prerequisites were relaxed for these four attempts
only: existing subscription, no retries, about ten minutes per review, no paid
API fallback, installation or infrastructure. The full study's original
requirements remain a separate future decision; its [template](RESULTS.md)
remains NOT RUN for that study.

## What ran

Four fresh coding-agent contexts (`fork_turns="none"`) ran serially:
**c01-A, c01-B, c03-B, c03-A**. No model/reasoning overrides were supplied;
all used the same existing host defaults. Resolved backend model/version,
reasoning level, sampling and seed are **UNKNOWN**, not the previously proposed
CLI configuration. No earlier output or feedback was sent to another reviewer.

Each pair received identical source packets and common task/safety instructions.
A was told to use ordinary review without optional audit skills; B received the
actual unchanged `faultline-audit/SKILL.md`. Exact [prompts](pilot/prompts/)
and verbatim final [reports](pilot/reports/) are retained. Temporary packet
paths can be reconstructed from [source-manifest.json](source-manifest.json).

| Case | Pinned public revision | Verification |
| --- | --- | --- |
| c01, AtomicSaver/atomic_save | `mahmoud/boltons@4e5faa3d7e4008d89e0d8bf1ea87b6d9a061a16d` | All 9 manifest files matched before/after |
| c03, TTLCache deadline/iteration | `tkem/cachetools@6f23e2a7b75a42d30cb9d890ab3ca4059ee01bfd` | All 10 manifest files matched before/after |

Packets came from PR #26's prepared whole-file source extractions. Expectations,
classifications, history and experiment documents were outside permitted reads.
Canonical skill: base `f0e090c1e5e3e0e442c81778617e8eb2cd271430`, SHA-256
`5644276b8b8c94840bf02c2a7700d6fa7091e25002d8ad39e37d4d08aca77438`;
repository and installed copies matched. B's setup added one instruction and
reading that existing 7,183-byte file. No installation or tuning was needed.

## Comparison for human assessment

All meaningfulness, source support, test practicality and false-positive grades
remain **PENDING**. These are observer notes to help assess each raw report.

| Review | Reported weakness / source support | Test proposal | Noise or uncertainty to assess |
| --- | --- | --- | --- |
| [c01-A](pilot/reports/c01-A.md) | Exit cleanup; part/destination collision; atomicity protection. `fileutils.py:335–490`; only saver unit test at `tests/test_fileutils.py:32` | Failing exit, colliding filename, body failure, completion-time overwrite race and existing part; uses file-test style | Calls two findings “source defects.” Keep suspected; exception precedence and collision rejection policy need assessment |
| [c01-B](pilot/reports/c01-B.md) | Exit cleanup and completion-time overwrite protection; both also in A. Same source/test plus rename helpers at `fileutils.py:301–320` | Concrete failing-`os.fsync` setup; competing destination created inside block; observable destination/part assertions | Separates suspected bug from protection gap; explicitly leaves simultaneous-exception precedence a contract question |
| [c03-B](pilot/reports/c03-B.md) | No actionable finding; cites deadline/lookup/expiration/bare-iteration tests at `tests/test_ttl.py:87,129,180,205` | No redundant test proposed | No alarm emitted; completeness of negative still needs assessment |
| [c03-A](pilot/reports/c03-A.md) | Candidate advancing-clock iteration gap; contrasts per-yield timer context (`src/cachetools/__init__.py:519–527`) with tests at `tests/test_ttl.py:180–203` | Reuses `Timer(auto=True)` and manual ticks for lookup-during-yield and expiry-between-yields; no real sleeps | Whether this protects a consequential supported contract or an implementation detail remains unresolved; no bug claimed |

Both c01 reports identify flush/fsync before close/cleanup and the unprotected
completion-time overwrite check. B gives a more concrete I/O-failure hook and
more careful confidence wording. A provides additional candidate scenarios.
Both recognize c03's existing deadline/stationary-iteration coverage; A's proposed
advancing-clock scenario is distinct. It does not invalidate the prepared
classification that the selected stationary behavior is protected. No additional
candidate is counted as an accepted win without human assessment.

## Time, effort and unknowns

Parent UTC samples immediately before dispatch and after receipt of each full
final report give approximate intervals, including dispatch/delivery/observer
delay. No timeout, failure, replacement or retry occurred. The ten-minute target
was instructed and observed, not enforced by a runner.

| Review | UTC start → final observed | Approx. elapsed | Input/cached/output/reasoning tokens | Cost |
| --- | --- | --- | --- | --- |
| c01-A | 05:40:32 → 05:41:37 | 65 s | UNKNOWN | UNKNOWN |
| c01-B | 05:41:37 → 05:42:40 | 63 s | UNKNOWN | UNKNOWN |
| c03-B | 05:42:40 → 05:43:27 | 47 s | UNKNOWN | UNKNOWN |
| c03-A | 05:43:27 → 05:44:35 | 68 s | UNKNOWN | UNKNOWN |

Total: about **4 min 3 s**; A 133 s, B 110 s. This does not establish a speed
advantage. The interface did not return usage, billing or separate skill-read
time. Shared preparation, preservation/comparison and human time were not
separately metered. UNKNOWN does not mean zero.

Access limits were instructed, not enforced through newly qualified isolation.
Contexts share a host and may see global skill metadata; A was told not to load
optional skills. The interface returned final reports without exported per-review
tool transcripts, so unseen reads/instruction exposure cannot be certified.
No reviewer reported a security/permission failure, execution or file changes;
post-review packet inventories/hashes were unchanged. This is not independent
proof of compliance or security qualification.

`grove` is both curator and human assessor; grading is not independent of curation.
Reports are arm-labeled, not blinded. The observer knew withheld expectations but
did not pass them to reviewers or supply human grades. Two convenience-selected
public cases, possible training exposure, unknown backend identity and pending
grades cannot establish general effectiveness or cost effectiveness.

## Owner disposition (2026-10-21)

The project owner reviewed the pilot summary and responded **"Looks good"**, then explicitly requested pragmatic finalization of draft PR #26. This is acceptance of the **bounded reporting and decision to keep Faultline unchanged**, not an independent source-level verdict on each report.

- **Recorded decision:** retain the provisional **NO CLEAR BENEFIT** finding from these two cases; do not tune the skill or launch further reviews as part of this PR.
- **Still unverified:** the proposed AtomicSaver defects, whether TTLCache's advancing-clock proposal is consequential, case-level human grades, token/cost figures, backend identity and actual isolation enforcement. Treat suspected runtime failures as hypotheses, not confirmed bugs.
- **Scope:** four completed read-only agent reviews, two public candidate scopes, unchanged original skill. The separate six-case RO-1 design and issue #6's executable-study prerequisites are not completed or waived.
- **Repository action:** close out the **documentation PR** after normal checks, but leave issue #6 open unless separately dispositioned by the maintainer.

This is an intentionally limited owner disposition, **not** a claim of fully independent human grading or general product effectiveness.

## Next decision

**Recommend option 3: keep Faultline unchanged because ordinary review supplied
similar core observations here.** Provisional **NO CLEAR BENEFIT** means no B-only
discovery appeared in these reports; accepted value remains for `grove` to assess.
Do not automatically expand, tune instructions or start another experiment.

Issue #6's executable three-arm study and #4/#5/#2 dependencies remain intact.
This pilot neither satisfies nor bypasses execution/security qualification.
No target code/tests/builds, mutation engine or fault injection ran, and no target
repository was modified. PR #26 remains draft; no merge or issue closure follows.
