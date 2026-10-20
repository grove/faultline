#!/usr/bin/env python3
"""Smoke-test the real skills CLI in disposable project directories.

This is a development check, not part of the installed audit skill. It downloads
the CLI, but never installs globally or runs a coding agent or target project.
By default it installs the current checkout; --source can verify a published ref
against the same checkout. Installation is not proof of host activation or audit
quality.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "faultline-audit"
AGENT_PATHS = {
    "codex": Path(".agents/skills") / SKILL_NAME,
    "claude-code": Path(".claude/skills") / SKILL_NAME,
}
INLINE_LINK = re.compile(r"\[[^\]\n]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)")
REFERENCE_LINK = re.compile(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(?:<([^>]+)>|(\S+))")


class InstallCheckError(RuntimeError):
    """A discovered or installed package does not meet the delivery contract."""


def payload(directory):
    """Record every delivered file, including supporting references."""
    directory = Path(directory).resolve()
    if not (directory / "SKILL.md").is_file():
        raise InstallCheckError(f"Missing skill entry point: {directory / 'SKILL.md'}")
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise InstallCheckError(f"Package contains a nonportable symlink: {path}")
        if path.is_file():
            files[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def check_relative_links(directory):
    """Check file links in shipped Markdown without relying on the source repo."""
    directory = Path(directory).resolve()
    for document in sorted(directory.rglob("*.md")):
        text = document.read_text(encoding="utf-8")
        # Examples in fenced code are not documentation dependencies.
        text = re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?^ {0,3}\1[ \t]*(?:\n|$)", "", text)
        for match in list(INLINE_LINK.finditer(text)) + list(REFERENCE_LINK.finditer(text)):
            target = next(group for group in match.groups() if group is not None)
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (document.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(directory):
                raise InstallCheckError(f"Link escapes installed package: {document.name} -> {target}")
            if not resolved.exists():
                raise InstallCheckError(f"Missing linked file: {document.name} -> {target}")


def verify_payload(source, installed):
    expected, actual = payload(source), payload(installed)
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
    if missing or extra or changed:
        raise InstallCheckError(
            f"Incomplete install at {installed}: missing={missing}, extra={extra}, changed={changed}"
        )
    check_relative_links(installed)
    return len(expected)


def run_cli(prefix, arguments, project, environment):
    command = prefix + arguments
    result = subprocess.run(
        command, cwd=project, env=environment, text=True, capture_output=True, timeout=120,
    )
    if result.returncode:
        raise InstallCheckError(
            f"skills command failed ({result.returncode}): {' '.join(arguments)}\n"
            f"{result.stdout[-4000:]}\n{result.stderr[-4000:]}"
        )
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(ROOT), help="Local path or published source; must match this checkout")
    parser.add_argument("--skills-version", default="latest", help="skills npm version or tag (default: latest)")
    parser.add_argument("--work-dir", type=Path, default=ROOT.parent, help="Parent for temporary project and npm cache directories")
    args = parser.parse_args()
    if Path(args.source).exists():
        args.source = str(Path(args.source).resolve())
    npx = shutil.which("npx")
    if not npx:
        raise InstallCheckError("npx is required; install Node.js >=22.20.0 to run this development check")
    source_package = ROOT / SKILL_NAME
    check_relative_links(source_package)
    payload(source_package)

    with tempfile.TemporaryDirectory(prefix="faultline-install-", dir=args.work_dir) as temporary:
        work = Path(temporary)
        environment = os.environ.copy()
        environment.update({
            "DISABLE_TELEMETRY": "1", "DO_NOT_TRACK": "1", "CI": "1",
            "INSTALL_INTERNAL_SKILLS": "0", "GIT_TERMINAL_PROMPT": "0",
            "NODE_DISABLE_COMPILE_CACHE": "1", "NO_COLOR": "1",
            "npm_config_update_notifier": "false",
        })
        prefix = [
            npx, "--yes", "--cache", str(work / "npm-cache"),
            "--package", f"skills@{args.skills_version}", "--", "skills",
        ]
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        version = run_cli(prefix, ["--version"], work, environment).strip()
        print(f"Node: {node_version}; skills CLI: {version}; source: {args.source}", flush=True)

        for mode in ("symlink", "copy"):
            project = work / mode
            project.mkdir()
            arguments = ["add", args.source, "--agent", *AGENT_PATHS, "--yes", "--json"]
            if mode == "copy":
                arguments.append("--copy")
            output = run_cli(prefix, arguments, project, environment)
            try:
                results = json.loads(output)
            except json.JSONDecodeError as error:
                raise InstallCheckError(f"Installer did not return its JSON result: {output[-4000:]}") from error
            if not isinstance(results, list) or len(results) != 1:
                raise InstallCheckError(f"Expected exactly one discoverable skill, got: {results}")
            result = results[0]
            expected = {"name": SKILL_NAME, "status": "installed", "scope": "project", "mode": mode}
            if any(result.get(key) != value for key, value in expected.items()):
                raise InstallCheckError(f"Unexpected installation result: {result}")
            for agent, relative in AGENT_PATHS.items():
                installed = project / relative
                if not installed.resolve().is_relative_to(project.resolve()):
                    raise InstallCheckError(f"Installation escapes disposable project: {installed}")
                if mode == "copy" and installed.is_symlink():
                    raise InstallCheckError(f"Copy installation unexpectedly created a symlink: {installed}")
                count = verify_payload(source_package, installed)
                print(f"  {mode}: {agent}: {count} matching files; local links resolve", flush=True)

            lock = json.loads((project / "skills-lock.json").read_text(encoding="utf-8"))
            if set(lock.get("skills", {})) != {SKILL_NAME}:
                raise InstallCheckError("Project lock must contain exactly faultline-audit")

    print("PASS: discovery, project installation, full payload, and local links. Host activation and audit quality were not tested.")


if __name__ == "__main__":
    try:
        main()
    except (InstallCheckError, OSError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
