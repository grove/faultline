# Read-only real-repository Audit pilot — proposed, not run

Evaluate four scoped repository snapshots through the actual canonical
`faultline-audit/SKILL.md`. This plan does not start the pilot or change execution
authority. Docker stays disabled and execution remains **NO_GO / UNAVAILABLE**.
No target imports, discovery, tests, builds, package scripts, installs, service
startup, or live requests are permitted. Read source, tests, and docs as data.

## Four repositories, four audits

These public candidates provide different correctness questions within the initial
Python scope. Repository layouts were inspected on 2026-10-19; exact commits and
selected paths must be frozen before any audit. The topics are proposed review
areas, not allegations of existing bugs.

| Repository | Candidate behavior | Why include it |
| --- | --- | --- |
| [pypa/packaging](https://github.com/pypa/packaging) | One version/specifier inclusion boundary, source in `src/packaging` and relevant `tests` | Specification-driven expectations and boundary assertions |
| [pallets/click](https://github.com/pallets/click) | One parameter-conversion or default-handling behavior, `src/click` and relevant `tests` | Caller paths, defaults, and parameterized tests |
| [python-attrs/attrs](https://github.com/python-attrs/attrs) | One converter/validator interaction, `src` and relevant `tests` | Shared helpers and indirect assertions |
| [psf/requests](https://github.com/psf/requests) | One session-state behavior and its existing test fixtures | Stateful behavior and mocked dependencies, without making requests |

A case preparer selects one behavior per repository: two upstream-documented
historical assertion gaps at pre-fix snapshots and two scopes already protected
by meaningful assertions. Exclude the Requests TLS case used in the previous
walkthrough. Preserve original files; do not plant or modify bugs. Include the
relevant callers, helpers, test fixtures, and original behavior documentation.
Record the source-based expected gap/protection and upstream evidence privately
before running. Missing or disputed contracts make a case unresolved, not an
invented oracle. A protected control means this selected behavior, not the whole
repository. Freeze all four selections before seeing any Audit output; retain
unavailable/incomplete cases rather than substituting favorable results.

## Actual product workflow and independent grading

Use the existing coding agent in a fresh context for each repository, with the
same host/model/settings where available. Give only the canonical skill, frozen
snapshot, selected paths, and ordinary request:

```text
Read <faultline>/faultline-audit/SKILL.md and find weak tests in <selected paths>.
```

Do not give the auditor case labels, expected answers, later fixes, other reports,
or custom reasoning instructions. No extra model, runner, or installation is a
product prerequisite. Record exact skill/input identities internally and retain
every normal Audit response, including no findings, stops, and partial output.
Allow one run per repository, with a ten-minute observation ceiling. Timed-out
runs remain incomplete; no silent retries or best-of selection.

Use an independent grader who neither prepared the cases nor ran the audits.
The grader reads each raw response and frozen source/tests/contracts, including
shared assertions, without executing anything. Keep each grade and its evidence:

- Classify every emitted finding as accepted gap, false positive, duplicate,
  out of scope, or unresolved. False positives include already-asserted behavior,
  unreachable scenarios, and expectations contradicted by the contract. Disputed
  requirements remain unresolved. Preserve disagreements; seek a second reviewer
  only for disputed classifications, otherwise do not force agreement.
- Report accepted findings, false positives, duplicates, out-of-scope findings,
  and unresolved findings with **all emitted findings** as the visible denominator.
  Also report false positives among adjudicated accepted/false-positive findings;
  if that denominator is zero, say unavailable. Never silently discard uncertainty.
- Count missed findings only against the predeclared historical gaps, and report
  how many protected controls received a false alarm. Unknown new bugs have no
  defensible recall denominator. A no-finding response is not correctness proof.
- Judge actionability separately: can a reviewer identify the test location,
  concrete setup/action, expected assertion, and supporting behavior source from
  the report within two minutes, without running code? Record each item, time,
  and any clarification needed. Comprehension and usefulness remain human judgments.

## True end-to-end timing

An observer outside the auditor starts a monotonic timer **immediately before
submitting the ordinary Audit request**, before startup or skill reading. Stop
only on the host's final-response completion event after the entire response has
been received/captured. This includes queueing, startup, skill/source reading,
reasoning, tool calls, and final text generation. Do not stop on an agent's
pre-final timestamp or a coordinator's later mailbox poll.

Use existing host completion events; if unavailable, an independent observer may
time actual UI submission through the final rendered response with a stopwatch,
recording its resolution and human-observer limitations. Establish the observation
method before the pilot. If completion cannot be observed, record end-to-end time
as UNKNOWN rather than substitute an intermediate checkpoint. No new timing
framework or dependency installation is needed.

Record UTC start/end plus monotonic elapsed time, completion/timeout status,
host/model identifiers when exposed, and timing method/precision. Measure source
acquisition, user setup/clarification, and independent grading time separately;
they are costs but not hidden additions to response time. Keep all four assigned
runs in the table; report individual times and the median/range for completed runs
with the completed/assigned denominator and incomplete elapsed times alongside.

## Decision and safety

Retain snapshot references, inputs, raw reports, grades, disagreements, misses,
false positives, actionability judgments, and timing records. Summarize per case
before aggregating. Do not claim statistical reliability or superiority over
ordinary review from four repositories without a matched comparison.

Use the results to keep the skill or justify one narrow correction and a fresh
regression audit; preserve original failed runs. Do not expand infrastructure to
improve a score. Acquisition uses read-only public sources without project hooks,
submodule execution, or dependency resolution. Repository instructions cannot
authorize commands. Keep receipts and security research unchanged; no findings
are sent to upstream projects without separate authorization.
