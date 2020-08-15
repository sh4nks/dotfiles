#!/usr/bin/env python3
"""
https://stackoverflow.com/questions/16787916/difference-between-two-directories-in-linux


"""
import os
import sys


def compare_dirs(d1, d2):
    def print_local(a, msg):
        print("DIR " if a[2] else "FILE", a[1], msg)

    # ensure validity
    for d in [d1, d2]:
        if not os.path.isdir(d):
            raise ValueError("not a directory: " + d)
    # get relative path
    l1 = [(x, os.path.join(d1, x)) for x in os.listdir(d1)]
    l2 = [(x, os.path.join(d2, x)) for x in os.listdir(d2)]
    # determine type: directory or file?
    l1 = sorted([(x, y, os.path.isdir(y)) for x, y in l1])
    l2 = sorted([(x, y, os.path.isdir(y)) for x, y in l2])
    i1 = i2 = 0
    common_dirs = []
    while i1 < len(l1) and i2 < len(l2):
        if l1[i1][0] == l2[i2][0]:  # same name
            if l1[i1][2] == l2[i2][2]:  # same type
                if l1[i1][2]:  # remember this folder for recursion
                    common_dirs.append((l1[i1][1], l2[i2][1]))
            else:
                print_local(l1[i1], "type changed")
            i1 += 1
            i2 += 1
        elif l1[i1][0] < l2[i2][0]:
            print_local(l1[i1], "removed")
            i1 += 1
        elif l1[i1][0] > l2[i2][0]:
            print_local(l2[i2], "added")
            i2 += 1
    while i1 < len(l1):
        print_local(l1[i1], "removed")
        i1 += 1
    while i2 < len(l2):
        print_local(l2[i2], "added")
        i2 += 1

    # compare subfolders recursively
    for sd1, sd2 in common_dirs:
        compare_dirs(sd1, sd2)


if __name__ == "__main__":
    compare_dirs(sys.argv[1], sys.argv[2])
