# PRs #18 and #19 — merge-readiness review, 2026-10-19

## Decision

[PR #18](https://github.com/grove/faultline/pull/18), reviewed at
`40cfeeafc816d5474db37cce6b014d7f7cab2ee0`: **ready for an approved merge**.
No code or documentation merge blocker found. Five focused checks pass.

[PR #19](https://github.com/grove/faultline/pull/19), evaluated at
`1302008ecb49fc9fea902e54300bd86a89ae35d7`: **ready as a follow-up to #18**.
Seven focused checks pass. Its current target is `feat/audit-first`, so the
remaining merge prerequisite is to land #18, retarget #19 to `main`, and recheck
the final diff and merge state. Do not merge #19 into the feature branch as a
substitute for that sequence. This review adds only this record, the
[real-repository pilot plan](real-repository-evaluation-plan.md), and a link from
the synthetic report; the evaluated skill, fixtures, raw outputs, grades, and
timings are unchanged.

Neither PR has been merged. No review record or readiness decision authorizes
merge: explicit user approval is still required. No execution scope is changed.

## Review evidence

For #18, checked the complete canonical skill, standalone copying/discovery
instructions, report fields and example, proposed-only Docker section, historical
archives, connected tests, and frozen-spike links. Repository/paths are sufficient
input; no runner or manifest is required. Findings require a concrete scenario,
test evidence, smallest assertion, and uncertainty. The skill forbids target
execution, imports/discovery/builds/installs, Docker probes, edits, repository-
supplied authority, and host-shell fallback. Existing host/tool qualification plus
caller authorization remain required; trust, installed Docker, and closed issues
cannot lift the advice-only release boundary. No launcher is added.

For #19, read all six fixture repositories and raw responses, the protocol,
expectations, manifests, results, and evidence tests. Recomputed fixture/report
identities and timing intervals; matched the recorded skill hash against its
exact original commit and current bytes. The three selected weaknesses and three
protected controls agree with source-only inspection. No test outcome is claimed.
Coordinator grading, tiny authored cases, shared-filesystem answer restrictions,
unknown exact model deployment, no repeatability/user study, and incomplete
end-to-end latency measurement are disclosed. Published 9–21-second intervals
are explicitly pre-response checkpoints, not full response times. Raw temporary
links are preserved as transcript data, with portable fixture links in the report.
The evidence is reproducible as inputs and a procedure, not a promise of identical
model responses or reproducible performance.

No necessary code fix was identified. Do not change the skill merely to add a
review diff. The next pilot separates case preparation, auditing, and independent
grading, and measures the completed final response rather than the checkpoint.

## Checks and limits

- #18: four `test_skill.py` checks plus the frozen-spike hash/syntax check pass.
- #19: those five plus both `test_audit_evaluation.py` checks pass. Fixture Python
  is parsed as text; none is imported or executed. These are offline evidence and
  packaging checks, not model-compliance tests.
- Skill-creator `quick_validate.py` was attempted in both checkouts and failed
  before validation with `ModuleNotFoundError: No module named 'yaml'`. No
  dependency was installed. Existing standard-library metadata checks passed.
- Local documentation targets/anchors and `git diff --check` pass. The historical
  qualification link pinned to the earlier commit resolves on GitHub.
- `ISOLATION.md`, qualification evidence, frozen experiments, and existing local
  work were compared against their preserved base/snapshot and remain unchanged.
  The skill and historical plans are unchanged by #19 and this review.
- At review time, both PRs are open, non-draft, conflict-free, and have no attached
  CI checks or GitHub reviews. REST branch/rules inspection reports no protection
  requirements for `main` or `feat/audit-first`. Local test results are not CI or
  an independent GitHub approval.

Docker, target-project code, qualification procedures, real-repository audits,
dependency installation, and merge operations were not run.

## Merge sequence after explicit approval

Prefer a merge commit for #18, which preserves the ancestor shared by the stacked
#19. Keep its feature branch while #19 is open. Then retarget #19 to `main` and
confirm its diff contains only evaluation evidence, checks, and these planning
notes, with no gate or qualification changes. Recheck the exact heads, focused
checks, and merge state before any separately approved merge of #19.

If #18 is squash-merged or rebased instead, first reconcile #19's base and review
the resulting diff; do not assume the stack is unchanged or force-push. No merge
method, branch retargeting, branch deletion, or force-push is performed by this
review. The outstanding prerequisite for both actual merges is user approval.
