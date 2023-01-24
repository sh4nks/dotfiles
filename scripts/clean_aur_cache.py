#!/usr/bin/env python3

import os
import sys


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def log(msg):
    print(msg + bcolors.ENDC)


CACHE_DIR = os.path.expanduser("~/.cache/pikaur")
FILE_ENDINGS = ".tar.xz .tar.gz .zip .deb .rpm .pkg.tar .tar.bz2".split()
EXCLUDED_DIRS = set([".git", "objects", "refs", "info", "hooks", "branches"])
DRY_RUN = False


def humansize(nbytes):
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ("%.2f" % nbytes).rstrip("0").rstrip(".")
    return bcolors.HEADER + f"{f} {suffixes[i]}" + bcolors.ENDC


def prompt_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n"
            )


def get_dir_size(root, files):
    dir_size = 0
    big_files = []

    if len(files) < 1:
        return dir_size, big_files

    for f in files:
        if not f.endswith(tuple(FILE_ENDINGS)):
            continue

        f_path = os.path.join(root, f)

        if os.path.islink(f_path):
            continue

        f_size = os.path.getsize(f_path)
        dir_size += f_size

        big_files.append((f, f_size))

    return dir_size, big_files


def get_files():
    sum_fsize = 0
    sum_f = {}
    for root, dirs, files in os.walk(CACHE_DIR, topdown=True):
        dirs[:] = [
            d
            for d in dirs
            # ignore git dirs
            if not d.startswith(".")
            and not d.endswith("-git")
            and d not in EXCLUDED_DIRS
        ]

        dir_size, big_files = get_dir_size(root, files)

        if dir_size > 0:
            sum_fsize += dir_size
            sum_f[root] = sorted(big_files)
            sum_f[root].append(dir_size)

    return sum_f, sum_fsize


def delete_files(files):
    for f in files:
        os.remove(f)


def main(dry_run=False, force=False):
    log(f"Using cache dir: {CACHE_DIR}")
    log(
        f"Looking for files with following file endings: "
        f"{', '.join(FILE_ENDINGS)}\n"
    )

    if not os.path.exists(CACHE_DIR):
        log(f"Cache directory does not exist: {CACHE_DIR}")
        return
    if not os.path.isdir(CACHE_DIR):
        log(f"{CACHE_DIR} is not a directory.")

    dirs, size = get_files()
    all_files = []
    for d in sorted(dirs.items(), key=lambda x: x[1][-1]):
        log(bcolors.OKBLUE + f"{d[0]} - {humansize(d[1][-1])}")
        for f in d[1][:-1]:
            log(f"  {os.path.basename(f[0])} - {humansize(f[1])}")
            all_files.append(os.path.join(d[0], f[0]))

    if size == 0:
        log("No deletable files found.")
        return

    log(
        f"\nCould reclaim {humansize(size)} of space by deleting "
        + bcolors.OKGREEN
        + f"{len(all_files)} files"
        + bcolors.ENDC
        + ".\n"
    )

    if dry_run:
        log(bcolors.WARNING + "No files deleted - dry run.")
        return

    if not force and not prompt_yes_no("Do you want to continue?"):
        return
    else:
        delete_files(all_files)
        log(
            bcolors.OKGREEN
            + f"{len(all_files)} files "
            + bcolors.ENDC
            + f"deleted and {humansize(size)} reclaimed"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean AUR cache.")
    parser.add_argument(
        "--force", action="store_true", help="Forcefully delete the files"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't delete any files"
    )
    args = parser.parse_args()

    main(args.dry_run, args.force)
