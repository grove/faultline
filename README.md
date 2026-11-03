# Faultline

**Before you merge, find important bugs your tests might miss.**

Faultline works with your existing coding agent. It reads your changes, follows
relevant code and tests, and suggests the smallest useful test for a realistic
failure. It does not change files or run tests. No project setup is needed.

## Install

In the project you want to check:

```sh
npx skills@latest add grove/faultline
```

Choose your coding agent in the installer. Installation needs Node.js and Git;
using Faultline needs no Docker, test runner, or additional service.
[Installation help](docs/usage.md#installation-help).

## Check my changes

Ask your coding agent:

```text
Use faultline-audit to check my changes.
```

Faultline starts with your local changes. On a clean feature branch, it checks
the branch changes against the locally available default branch. It tells you
what it reviewed and asks one short question if the comparison is unclear.
You do not need to choose tests, provide hashes, or configure a runner.
In Codex, select **Faultline** in the skill picker or use `$faultline-audit`.

To focus on a behavior instead, ask:

```text
Use faultline-audit to check whether retries could charge twice.
```

## What you get

Up to three findings, with the most important first. Each explains a realistic
failure, why the existing tests could miss it, and a concrete test to add.
Links point to the code and tests actually read; suspected bugs and test gaps
are distinguished, with important uncertainty stated.

Illustrative only; this example is not an observed bug or an executed test:

> **A retry could charge twice**
>
> If a charge succeeds but its response is lost, retrying appears to record a
> second charge. The existing test checks only a successful first request.
>
> **Suggested test:** lose the response after recording the charge, retry with
> the same key, and assert one recorded charge.
>
> **Status:** suspected bug; a shared deduplication layer could prevent this.
>
> Reviewed payment retry changes and their tests. Tests were not run.

If nothing useful turns up, Faultline says **No actionable finding in the reviewed
scope**, with a short reason. That is not a guarantee that the project is correct.

Continue in the same conversation: “Explain this finding” or “Show me the proposed
test.” A proposed test is not written to disk or run.

[More examples and optional GitHub issues](docs/usage.md) ·
[Maintainer guide and research](docs/maintaining.md) · [License](LICENSE)
