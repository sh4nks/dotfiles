#!/usr/bin/env python3

import os
import sys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log(msg):
    print(msg + bcolors.ENDC)


CACHE_DIR = os.path.expanduser("~/.cache/yay")
FILE_ENDINGS = ".tar.gz .zip .deb .rpm .pkg.tar".split()
DRY_RUN = False

log(f"Using cache dir: {CACHE_DIR}")
log(f"Looking for following file endings: {', '.join(FILE_ENDINGS)}\n")


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return bcolors.HEADER + f'{f} {suffixes[i]}' + bcolors.ENDC


def prompt_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
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
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def gather_files():
    sum_fsize = 0
    dir_size = 0
    sum_f = {}
    for d in os.listdir(CACHE_DIR):
        dir_size = 0
        d = os.path.join(CACHE_DIR, d)

        if os.path.isfile(d):
            continue

        # gather all files + size
        for f in os.listdir(d):
            f = os.path.join(d, f)
            if not f.endswith(tuple(FILE_ENDINGS)):
                continue

            f_size = os.path.getsize(f)
            dir_size += f_size
            sum_fsize += f_size

            try:
                sum_f[d].append((f, f_size))
            except (AttributeError, KeyError):
                sum_f[d] = [(f, f_size)]

        # add dir size
        if d is not None:
            # will error when dir has no deletable files
            try:
                sum_f[d].append(dir_size)
            except KeyError:
                pass

    return sum_f, sum_fsize


def delete_files(files):
    for f in files:
        os.remove(f)


def main(dry_run=False):
    if not os.path.exists(CACHE_DIR):
        log(f"Cache directory does not exist: {CACHE_DIR}")
        return
    if not os.path.isdir(CACHE_DIR):
        log(f"{CACHE_DIR} is not a directory.")

    dirs, size = gather_files()
    all_files = []
    for d in sorted(dirs.items(), key=lambda x: x[1][-1]):
        log(bcolors.OKBLUE + f"{d[0]} - {humansize(d[1][-1])}")
        for f in d[1][:-1]:
            log(f"  {os.path.basename(f[0])} - {humansize(f[1])}")
            all_files.append(f)

    log(f"\nCould reclaim {humansize(size)} of space by deleting " +
        bcolors.OKGREEN + f"{len(all_files)} files" + bcolors.ENDC + ".\n")

    if prompt_yes_no("Do you want to continue?"):
        if dry_run:
            log("\n" + bcolors.WARNING + "No files are going to be deleted "
                "- dry run.")
            return

        delete_files(all_files)
        log(bcolors.OKGREEN + f"{len(all_files)} files " + bcolors.ENDC +
            f"deleted and {humansize(size)} reclaimed")


if __name__ == "__main__":
    dry_run = False
    if len(sys.argv) > 1 and sys.argv[1] == "dryrun":
        dry_run = True

    main(dry_run)
