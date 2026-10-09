#!/usr/bin/env python3
import argparse
import curses
import difflib
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import tomllib

WORKSPACE = Path.cwd()
TAG_PATTERN = re.compile(r"v\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?")
CHANGELOG_NAMES = ("CHANGELOG.md", "CHANGES")
CHANGELOG_HEADER = """\
Changelog
=========

Here you can see the full list of changes between each release.

"""
MAX_COMMITS_SHOWN = 10
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def ansi(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(text):
    return ansi("1", text)


def dim(text):
    return ansi("2", text)


def red(text):
    return ansi("31", text)


def green(text):
    return ansi("32", text)


def yellow(text):
    return ansi("33", text)


def cyan(text):
    return ansi("36", text)


def run_git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )


def git(repo, *args):
    result = run_git(repo, *args)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.rstrip()


def confirm(question):
    return input(f"{bold(question)} [y/N] ").strip().lower() in ("y", "yes")


def find_plugins():
    return sorted(
        path
        for path in WORKSPACE.glob("flaskbb-plugin-*")
        if (path / ".git").exists() and (path / "pyproject.toml").exists()
    )


def read_pyproject(repo):
    with open(repo / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def latest_tag(repo):
    return run_git(repo, "describe", "--tags", "--abbrev=0").stdout.strip() or None


def tag_exists(repo, tag):
    return bool(run_git(repo, "rev-parse", "-q", "--verify", f"refs/tags/{tag}").stdout)


def suggest_tag(repo):
    version = read_pyproject(repo)["project"]["version"]
    if tag_exists(repo, f"v{version}"):
        version = re.sub(r"\d+$", lambda match: str(int(match[0]) + 1), version)
    return f"v{version}"


def uncommitted_changes(repo):
    output = git(repo, "status", "--porcelain", "--untracked-files=all")
    return [(line[:2], line[3:]) for line in output.splitlines()]


def overview_row(repo):
    version = read_pyproject(repo)["project"]["version"]
    tag = latest_tag(repo) or "-"
    branch = git(repo, "branch", "--show-current")
    row = f"{repo.name:<30} {version:<10} {tag:<12} {suggest_tag(repo):<12} {branch:<7}"
    return row, bool(uncommitted_changes(repo))


def pick_plugins(screen, plugins, rows):
    curses.curs_set(0)
    green_color = yellow_color = curses.A_NORMAL
    if USE_COLOR and curses.has_colors():
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        green_color = curses.color_pair(1)
        yellow_color = curses.color_pair(2)
    selected = set()
    cursor = 0
    while True:
        width = screen.getmaxyx()[1] - 1
        screen.erase()
        screen.addnstr(
            0,
            0,
            "Space toggles a plugin, enter releases, q quits.",
            width,
            curses.A_DIM,
        )
        screen.addnstr(
            2,
            0,
            f"    {'plugin':<30} {'version':<10} {'latest tag':<12} {'next':<12} branch",
            width,
            curses.A_BOLD,
        )
        for index, (row, dirty) in enumerate(rows):
            mark = "x" if index in selected else " "
            highlight = curses.A_REVERSE if index == cursor else curses.A_NORMAL
            row_color = green_color if index in selected else curses.A_NORMAL
            line = f"[{mark}] {row}"
            screen.addnstr(3 + index, 0, line, width, highlight | row_color)
            if dirty and len(line) < width:
                screen.addnstr(
                    3 + index,
                    len(line),
                    " (uncommitted changes)",
                    width - len(line),
                    highlight | yellow_color,
                )
        key = screen.getch()
        if key in (curses.KEY_UP, ord("k")):
            cursor = (cursor - 1) % len(rows)
        elif key in (curses.KEY_DOWN, ord("j")):
            cursor = (cursor + 1) % len(rows)
        elif key == ord(" "):
            selected ^= {cursor}
        elif key in (curses.KEY_ENTER, ord("\n"), ord("\r")):
            return [plugins[index] for index in sorted(selected or {cursor})]
        elif key == ord("q"):
            return []


def choose_plugins(plugins):
    rows = [overview_row(repo) for repo in plugins]
    return curses.wrapper(pick_plugins, plugins, rows)


def tracking_branch(repo):
    branch = git(repo, "branch", "--show-current")
    if not branch:
        sys.exit(f"{repo.name} is not on a branch.")
    upstream = run_git(
        repo, "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"
    ).stdout.strip()
    if not upstream:
        sys.exit(f"Branch {branch} of {repo.name} has no upstream branch.")
    remote, _, upstream_branch = upstream.partition("/")
    return branch, remote, upstream_branch


def show_status(repo, changes):
    tag = latest_tag(repo)
    commits = git(repo, "log", "--oneline", f"{tag}..HEAD" if tag else "HEAD")
    commits = commits.splitlines()
    version = read_pyproject(repo)["project"]["version"]
    print(f"  version in pyproject.toml: {bold(version)}")
    print(f"  latest tag:                {bold(tag or '-')}")
    print(f"  commits since {tag or 'the start'}: {bold(len(commits))}")
    for commit in commits[:MAX_COMMITS_SHOWN]:
        sha, _, subject = commit.partition(" ")
        print(f"    {yellow(sha)} {subject}")
    if len(commits) > MAX_COMMITS_SHOWN:
        print(dim("    ..."))
    if changes:
        print(yellow("  uncommitted changes:"))
        for status, path in changes:
            print(f"    {red(status)} {path}")


def ask_tag(repo):
    suggested = suggest_tag(repo)
    while True:
        answer = input(f"\n{bold('New tag')} [{green(suggested)}]: ").strip()
        answer = answer or suggested
        tag = answer if answer.startswith("v") else f"v{answer}"
        if not TAG_PATTERN.fullmatch(tag):
            print(red(f"{answer} is not a version tag like v1.2.3 or v3.0.0rc1."))
        elif tag_exists(repo, tag):
            print(red(f"Tag {tag} already exists."))
        else:
            return tag


def check_remote(repo, remote, upstream_branch, tag):
    output = git(
        repo, "ls-remote", remote, f"refs/heads/{upstream_branch}", f"refs/tags/{tag}"
    )
    remote_refs = {
        name: sha for sha, name in (line.split("\t") for line in output.splitlines())
    }
    if f"refs/tags/{tag}" in remote_refs:
        sys.exit(f"Tag {tag} already exists on {remote}.")
    remote_head = remote_refs.get(f"refs/heads/{upstream_branch}")
    is_behind = (
        remote_head
        and run_git(repo, "merge-base", "--is-ancestor", remote_head, "HEAD").returncode
    )
    if is_behind:
        sys.exit(f"{remote}/{upstream_branch} has commits you don't have. Pull first.")


def set_project_version(edits, repo, version):
    text = (repo / "pyproject.toml").read_text()
    new_text = re.sub(
        r'^version = "[^"]*"$',
        f'version = "{version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if new_text != text:
        edits["pyproject.toml"] = new_text


def ordinal(day):
    if 11 <= day % 100 <= 13:
        return f"{day}th"
    return f"{day}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th') }"


def changelog_name(repo):
    return next(
        (name for name in CHANGELOG_NAMES if (repo / name).exists()),
        CHANGELOG_NAMES[0],
    )


def released_on():
    today = datetime.now(UTC).astimezone().date()
    return f"Released on {today:%B} {ordinal(today.day)}, {today.year}"


def changelog_section(repo, version):
    tag = latest_tag(repo)
    subjects = git(
        repo, "log", "--no-merges", "--format=%s", f"{tag}..HEAD" if tag else "HEAD"
    )
    entries = [
        f"* {subject[:1].upper()}{subject[1:]}" for subject in subjects.splitlines()
    ]
    heading = f"Version {version}"
    lines = [heading, "-" * len(heading), "", released_on()]
    if entries:
        lines += ["", *entries]
    return "\n".join(lines) + "\n"


def update_changelog(edits, repo, version):
    name = changelog_name(repo)
    path = repo / name
    if not path.exists():
        edits[name] = CHANGELOG_HEADER + changelog_section(repo, version)
        return f"No changelog found, {name} is generated from the commit messages."
    text = path.read_text()
    heading = rf"^Version {re.escape(version)}\n-+\n\n"
    if not re.search(heading, text, flags=re.MULTILINE):
        section = changelog_section(repo, version)
        newest = re.search(r"^Version .+\n-+\n", text, flags=re.MULTILINE)
        if newest:
            edits[name] = (
                f"{text[: newest.start()]}{section}\n\n{text[newest.start() :]}"
            )
        else:
            edits[name] = f"{text.rstrip()}\n\n{section}"
        return (
            f"{name} has no 'Version {version}' section, it is generated from the "
            "commit messages."
        )
    new_text = re.sub(
        rf"({heading})Unreleased$",
        rf"\g<1>{released_on()}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if new_text != text:
        edits[name] = new_text
    return None


def plan_edits(repo, version):
    edits = {}
    set_project_version(edits, repo, version)
    note = update_changelog(edits, repo, version)
    if note:
        print(yellow(f"\n{note}"))
    return edits


def release_workflow_url(repo, remote):
    url = git(repo, "remote", "get-url", remote)
    match = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return match and f"https://github.com/{match[1]}/actions/workflows/release.yml"


def print_diff(relpath, old_text, new_text):
    lines = difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        f"a/{relpath}",
        f"b/{relpath}",
        lineterm="",
    )
    for index, line in enumerate(lines):
        if index < 2:
            print(bold(line))
        elif line.startswith("@@"):
            print(cyan(line))
        elif line.startswith("+"):
            print(green(line))
        elif line.startswith("-"):
            print(red(line))
        else:
            print(line)


def release(repo, dry_run):
    branch, remote, upstream_branch = tracking_branch(repo)
    changes = uncommitted_changes(repo)
    show_status(repo, changes)

    tag = ask_tag(repo)
    version = tag.removeprefix("v")
    check_remote(repo, remote, upstream_branch, tag)
    edits = plan_edits(repo, version)

    version_files = {"pyproject.toml", changelog_name(repo), "uv.lock"}
    dirty_paths = {path for _, path in changes}
    release_paths = sorted(edits.keys() | (dirty_paths & version_files))
    other_paths = sorted(dirty_paths - set(release_paths))
    include_others = bool(other_paths) and confirm(
        f"\nInclude the other {len(other_paths)} uncommitted change(s) "
        "listed above in the release commit?"
    )
    commit_paths = sorted(
        {*release_paths, "uv.lock", *(other_paths if include_others else ())}
    )
    push_command = [
        "git",
        "push",
        "--atomic",
        remote,
        f"{branch}:{upstream_branch}",
        tag,
    ]

    print(bold(f"\nRelease {repo.name} {green(tag)}"))
    print(f"  run uv lock, then commit 'version {version}' on {branch} with:")
    for path in commit_paths:
        if path in dirty_paths:
            note = yellow(" (includes your uncommitted changes)")
        elif path == "uv.lock":
            note = dim(" (if uv lock changes it)")
        else:
            note = ""
        print(f"    {path}{note}")
    print(f"  annotated tag {green(tag)}: 'release version {tag}'")
    print(f"  {cyan(' '.join(push_command))}")
    for relpath, new_text in edits.items():
        path = repo / relpath
        print()
        print_diff(relpath, path.read_text() if path.exists() else "", new_text)

    if dry_run:
        print(yellow("\nDry run, nothing was changed."))
        return
    if not confirm("\nProceed?"):
        sys.exit("Aborted.")

    for relpath, new_text in edits.items():
        (repo / relpath).write_text(new_text)
    print()
    if subprocess.run(["uv", "lock"], cwd=repo, check=False).returncode != 0:
        sys.exit(
            "\nuv lock failed. Nothing was committed, the edits above are left "
            f"uncommitted in {repo}."
        )
    release_paths = sorted(
        version_files & {path for _, path in uncommitted_changes(repo)}
    )
    if include_others:
        git(repo, "add", "--all")
        git(repo, "commit", "-m", f"version {version}")
    elif release_paths:
        git(repo, "add", "--", *release_paths)
        git(repo, "commit", "-m", f"version {version}", "--", *release_paths)
    git(repo, "tag", "-a", tag, "-m", f"release version {tag}")

    if subprocess.run(push_command, cwd=repo, check=False).returncode != 0:
        sys.exit(
            "\nPush failed. The commit and tag only exist locally. Retry with:\n"
            f"  cd {repo} && {' '.join(push_command)}"
        )
    print(green(f"\nPushed {branch} and {tag} to {remote}."))
    url = release_workflow_url(repo, remote)
    if url:
        print(
            f"The release workflow now publishes {tag} to PyPI and GitHub:\n"
            f"  {cyan(url)}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Bump, commit, tag and push releases of FlaskBB plugins "
        "in the current directory."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would happen without changing or pushing anything",
    )
    args = parser.parse_args()

    plugins = find_plugins()
    if not plugins:
        sys.exit(f"No flaskbb-plugin-* repositories found in {WORKSPACE}.")
    repos = choose_plugins(plugins)
    if not repos:
        sys.exit("Aborted.")
    for number, repo in enumerate(repos, 1):
        print(bold(cyan(f"\n=== [{number}/{len(repos)}] {repo.name} ===")))
        release(repo, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        sys.exit(red("\nAborted."))
    except SystemExit as error:
        sys.exit(red(error.code) if isinstance(error.code, str) else error.code)
