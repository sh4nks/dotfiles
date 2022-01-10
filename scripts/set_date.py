#!/bin/env python
import datetime
import os
import pprint


def set_file_last_modified(fname, dt):
    dt_epoch = dt.timestamp()
    os.utime(fname, (dt_epoch, dt_epoch))


def get_files(path, include=["jpg"]):
    files = os.listdir(path)
    relevant_files = []
    include_tuple = tuple(include)
    for fname in files:
        if fname.lower().endswith(include_tuple):
            relevant_files.append(fname)
    return sorted(relevant_files)


def main(path):
    files = get_files(path)
    for fname in files:
        # DSC_5358-126.JPG --> 1
        nr = int(fname.split("-")[1].split(".")[0])
        delta = str(datetime.timedelta(hours=12, seconds=nr))
        dt = datetime.datetime.fromisoformat(f"2021-07-31 {delta}")

        #print(f"{fname}\t\t{dt}")
        set_file_last_modified(fname, dt)

if __name__ == "__main__":
    #pprint.pprint(get_files("."))
    main(".")
