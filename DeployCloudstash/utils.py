#!/bin/python

import shlex
import time
from config import DEBUG, VERBOSE
from subprocess import run, PIPE, CompletedProcess, CalledProcessError
from pprint import pprint


def log(message: str, error: bool = False) -> None:
    # TODO write to a specific log file?
    #  timestamp = time.ctime()
    timestamp = time.strftime("%Y-%d/%m-%H:%M:%S", time.localtime())
    if error:
        print(f"{timestamp}|ERROR| {message}")
    else:
        print(f"{timestamp}| {message}")


def shell(cmd: str, context: str = None) -> CompletedProcess:
    # run a shell command

    # use shlex.split to split command string on spaces to a list of strings
    cmd_list = shlex.split(cmd)

    if DEBUG:
        print("---DEBUG")
        print("shell cmd:", cmd)
        if context is not None:
            print("context:", context)
        pprint(cmd_list)
        print("---DEBUG_END")

    try:
        # create the process, pipe stdout/stderr, output stdout/stderr as strings
        # add 'check=True' to throw an exception on a non-zero exit code
        if context is None:
            proc = run(cmd_list, stdout=PIPE, text=True)
        else:
            proc = run(cmd_list, stdout=PIPE, cwd=context, text=True)
    except (OSError, ValueError, CalledProcessError) as err:
        print("---")
        print(f"ERROR: Encountered an error executing the shell command: {cmd}")
        print("---")
        raise err

    # return the completed process
    return proc
