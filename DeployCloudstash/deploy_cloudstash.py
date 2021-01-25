#!/bin/python

import shlex
from subprocess import run, PIPE, CompletedProcess, CalledProcessError
from pprint import pprint

# enable/disable debug prints
DEBUG = True


def shell(cmd: str) -> CompletedProcess:
    # run a shell command

    # use shlex.split to split command string on spaces to a list of strings
    cmd_list = shlex.split(cmd)

    if DEBUG:
        print("---")
        print("shell cmd:", cmd)
        pprint(cmd_list)
        print("---")

    try:
        # create the process, pipe stdout/stderr, output stdout/stderr as strings, throw exception on errors
        proc = run(cmd_list, stdout=PIPE, text=True, check=True)
    except (OSError, ValueError, CalledProcessError) as err:
        print("---")
        print(f"ERROR: Encountered an error executing the shell command: {cmd}")
        print("---")
        raise err

    # return the completed process
    return proc


res = shell("echo foo")
print(res.stdout)
