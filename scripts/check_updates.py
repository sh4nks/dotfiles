#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["packaging", "tomlkit"]
# ///
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import tomlkit
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

PYPI_URL = "https://pypi.org/pypi/{}/json"
LOWER_BOUND_OPERATORS = (">=", "==", "~=", "===")

RED, CYAN, GREEN, RESET = "\033[31m", "\033[36m", "\033[32m", "\033[0m"
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def requirement_arrays(doc):
    project = doc.get("project", {})
    if "dependencies" in project:
        yield "project.dependencies", project["dependencies"]
    for extra, array in project.get("optional-dependencies", {}).items():
        yield f"project.optional-dependencies.{extra}", array
    for group, array in doc.get("dependency-groups", {}).items():
        yield f"dependency-groups.{group}", array


def pinned_items(doc):
    for _, array in requirement_arrays(doc):
        for index, item in enumerate(array):
            if not isinstance(item, str):
                continue
            req = Requirement(item)
            spec = next((s for s in req.specifier if s.operator in LOWER_BOUND_OPERATORS), None)
            if spec:
                yield array, index, req, spec


def pinned_requirements(doc) -> dict[str, tuple[str, str, Version]]:
    pinned = {}
    for _, _, req, spec in pinned_items(doc):
        pinned.setdefault(
            canonicalize_name(req.name),
            (req.name, spec.operator, Version(spec.version)),
        )
    return pinned


def upgrade(doc, upgrades: dict[str, Version]) -> None:
    for array, index, req, spec in pinned_items(doc):
        latest = upgrades.get(canonicalize_name(req.name))
        if latest:
            pattern = rf"({re.escape(spec.operator)}\s*){re.escape(spec.version)}"
            array[index] = re.sub(pattern, rf"\g<1>{latest}", array[index], count=1)


def has_comments(array) -> bool:
    text = array.as_string()
    for item in array:
        text = text.replace(item.as_string(), "", 1)
    return "#" in text


def sort_dependencies(doc) -> list[str]:
    # Items are moved between slots, so comments would stay behind; skip those arrays.
    skipped = []
    for label, array in requirement_arrays(doc):
        indices = [i for i, item in enumerate(array) if isinstance(item, str)]
        current = [array[i] for i in indices]
        ordered = sorted(current, key=lambda s: canonicalize_name(Requirement(s).name))
        if ordered == current:
            continue
        if has_comments(array):
            skipped.append(label)
            continue
        for index, item in zip(indices, ordered, strict=True):
            array[index] = item
    return skipped


def fetch_latest(name: str) -> Version | None:
    try:
        with urllib.request.urlopen(PYPI_URL.format(name), timeout=15) as resp:
            return Version(json.load(resp)["info"]["version"])
    except (urllib.error.URLError, InvalidVersion, KeyError, TimeoutError):
        return None


def target_version(operator: str, current: Version, latest: Version) -> Version:
    # ~= is precision sensitive: ~=8.0 allows 8.*, ~=8.5.0 only 8.5.*
    if operator == "~=":
        size = len(current.release)
        return Version(".".join(map(str, (latest.release + (0,) * size)[:size])))
    return latest


def colorize_diff(current: Version, latest: Version) -> str:
    text = str(latest)
    if not USE_COLOR:
        return text

    width = max(len(current.release), len(latest.release))
    cur = current.release + (0,) * (width - len(current.release))
    new = latest.release + (0,) * (width - len(latest.release))
    first_diff = next((i for i in range(width) if cur[i] != new[i]), width)

    if first_diff == 0 or (first_diff == 1 and new[0] == 0):
        color = RED
    elif first_diff == 1:
        color = CYAN
    else:
        color = GREEN

    parts = text.split(".")
    split_at = min(first_diff, len(parts) - 1)
    head = ".".join(parts[:split_at])
    tail = ".".join(parts[split_at:])
    return f"{head}{'.' if head else ''}{color}{tail}{RESET}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare pinned dependencies in pyproject.toml with the latest PyPI releases."
    )
    parser.add_argument(
        "pyproject", nargs="?", type=Path, default=Path("pyproject.toml")
    )
    parser.add_argument(
        "-u",
        "--upgrade",
        action="store_true",
        help="rewrite pyproject.toml with the latest versions",
    )
    parser.add_argument(
        "-s",
        "--sort",
        action="store_true",
        help="sort the dependencies in pyproject.toml alphabetically",
    )
    args = parser.parse_args()

    path = args.pyproject.resolve()
    print(f"Checking {path}")

    text = path.read_text()
    doc = tomlkit.parse(text)
    pinned = pinned_requirements(doc)

    with ThreadPoolExecutor(max_workers=16) as pool:
        latest_versions = dict(zip(pinned, pool.map(fetch_latest, pinned), strict=True))

    outdated = []
    upgrades = {}
    failed = []
    for key, (name, operator, current) in sorted(pinned.items()):
        latest = latest_versions[key]
        if latest is None:
            failed.append(name)
            continue
        target = target_version(operator, current, latest)
        if target > current:
            outdated.append((name, f"{operator}{current}", operator, current, target))
            upgrades[key] = target

    print()
    if outdated:
        name_w = max(len(row[0]) for row in outdated)
        cur_w = max(len(row[1]) for row in outdated)
        new_w = max(len(row[2]) + len(str(row[4])) for row in outdated)
        for name, current_spec, operator, current, latest in outdated:
            padding = " " * (new_w - len(operator) - len(str(latest)))
            new_spec = f"{padding}{operator}{colorize_diff(current, latest)}"
            print(f" {name:<{name_w}}  {current_spec:>{cur_w}}  ->  {new_spec}")
    else:
        print("All dependencies match the latest package versions :)")

    if failed:
        print(f"\nCould not fetch: {', '.join(failed)}", file=sys.stderr)

    if upgrades and args.upgrade:
        upgrade(doc, upgrades)
    skipped = sort_dependencies(doc) if args.sort else []

    new_text = tomlkit.dumps(doc)
    if new_text != text:
        path.write_text(new_text)

    if upgrades and args.upgrade:
        print(f"\nUpgraded {path}")
        print("Run uv lock to update uv.lock.")
    elif upgrades:
        print(f"\nRun {sys.argv[0]} -u to upgrade {path.name}")

    if args.sort:
        print(f"\nSorted dependencies in {path}")
        for label in skipped:
            print(f"Skipped {label}: it contains comments")

    print()
    return 1 if upgrades and not args.upgrade else 0


if __name__ == "__main__":
    sys.exit(main())
