# More ways to use Faultline

Start with [Check my changes](../README.md). Everything below is optional.

## Choose a scope

Use the same skill for each request; there are no modes to configure.

| When | Ask your coding agent |
| --- | --- |
| Before a commit or merge | `Use faultline-audit to check my changes.` |
| For a critical behavior | `Use faultline-audit to check whether retries could charge twice.` |
| For an unfamiliar area | `Use faultline-audit to find important bugs the tests might miss in payments/.` |
| For a broader review | `Use faultline-audit to find important bugs my tests might miss in this repository.` |

An explicit path, behavior, commit range, or pull-request diff takes precedence.
Otherwise, Faultline reviews staged and unstaged changes plus relevant untracked
source/tests. With a clean working tree on a feature branch, it uses the branch
changes against a locally identifiable default branch. It reports the comparison
it used. It does not fetch branches or require a GitHub connection.

If there are no changes, no Git metadata, or no clear comparison, Faultline asks
which path or behavior to check. It does not silently review the whole repository
or treat a missing diff as evidence that the code is protected.

Faultline follows relevant callers and tests beyond the changed lines when
needed. A finding is limited to the scope actually read. An unreadable file or
missing test is a stated limitation, not a clean result.

## Continue from a finding

Stay in the same conversation. Ask “Explain why the existing test misses this”
or “Show me the proposed test.” Faultline can outline the test in the project's
style in chat; it does not write a file or run the test. A code sketch is a
proposal, not a reproduced bug. Implementing and running it is a separate task
for your coding agent under its normal permissions.

If asked to verify a finding, Faultline says **Verification is not enabled;
here is the suggested test.** No Docker setup is needed for using Faultline.

## Turn a finding into a GitHub issue

Ask “Draft an issue for this finding” to get a draft in the conversation. No extra
skill is needed. The draft must preserve the source evidence, uncertainty, and
proposed test; it is not published.

For an optional guided GitHub publishing workflow, install
[Intentline's issue skill](https://github.com/grove/intentline) in the same project:

```sh
npx skills@latest add grove/intentline --skill intentline-issue
```

Stay in the **same coding-agent conversation** after reviewing a useful finding.
You do not need to rerun Faultline or copy its report.

**Prepare — review only:**

```text
Use intentline-issue in REVIEW mode to draft one GitHub issue from the
Faultline finding above. Recheck its evidence and expected behavior,
include acceptance criteria and a proposed test, and preserve uncertainty.
Don't publish or change anything.
```

**Publish — only after approving that draft:**

```text
Use intentline-issue in CREATE mode to publish the approved draft as
exactly one issue in OWNER/REPO. I authorize creating this one issue.
Check for duplicates, read back the new issue, and return its URL.
Do not change code or run tests.
```

Replace `OWNER/REPO` with the intended GitHub repository. Publishing requires
your coding agent's existing GitHub issue-write access; installation grants none.
Repeat the review and explicit CREATE request for each additional finding.
Suggested tests remain **PROPOSED — NOT RUN**.

## Installation help

The installer needs [Node.js 22.20.0 or newer](https://www.skills.sh/docs/cli)
and Git. Neither Node.js nor Docker is needed for the audit itself.

In Codex, you can explicitly invoke `$faultline-audit`. For other coding agents,
follow their skill invocation instructions. If the installed skill is not visible,
start a new agent session. To inspect discovery:

```sh
npx skills@latest add grove/faultline --list
```

### Manual installation

If you cannot use the `npx` installer but already have a Faultline checkout,
copy the same standalone skill into another project. Run this from the Faultline
checkout, replacing the target. It refuses to overwrite an existing installation:

```sh
target=/absolute/path/to/your/project
mkdir -p "$target/.agents/skills" &&
  test ! -e "$target/.agents/skills/faultline-audit" &&
  test ! -L "$target/.agents/skills/faultline-audit" &&
  cp -R faultline-audit "$target/.agents/skills/faultline-audit"
```

Installed copies are user-owned; recopy deliberately for updates. The repository
keeps [one canonical skill](../faultline-audit/SKILL.md), also used by the `skills` CLI.
No sibling project, hidden runtime, or installation-time code execution is required.
