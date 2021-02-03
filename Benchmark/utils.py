#!/bin/python

from subprocess import run, PIPE, CompletedProcess, CalledProcessError
import shlex
import time
from pprint import pprint
from config import GlobalConfig

# get config singleton
config = GlobalConfig.get()


def log(message: str, error: bool = False) -> None:
    # TODO write to a specific log file?
    #  timestamp = time.ctime()
    timestamp = time.strftime("%Y %d/%m %H:%M:%S", time.localtime())
    if error:
        print(f"{timestamp}|ERROR| {message}")
    else:
        print(f"{timestamp}| {message}")


def shell(cmd: str, context: str = None, env: dict = None) -> CompletedProcess:
    # run a shell command

    # use shlex.split to split command string on spaces to a list of strings
    cmd_list = shlex.split(cmd)

    if config.DEBUG:
        print("---DEBUG")
        print("shell cmd:", cmd)
        if context is not None:
            print("context:", context)
        if env is not None:
            print("env")
            pprint(env)
        pprint(cmd_list)
        print("---DEBUG_END")

    try:
        # create the process, pipe stdout/stderr, output stdout/stderr as strings
        # add 'check=True' to throw an exception on a non-zero exit code
        if context is None:
            proc = run(cmd_list, env=env, stdout=PIPE, text=True)
        else:
            proc = run(cmd_list, env=env, stdout=PIPE, cwd=context, text=True)
    except (OSError, ValueError, CalledProcessError) as err:
        print("---")
        print(f"ERROR: Encountered an error executing the shell command: {cmd}")
        print("---")
        raise err

    # return the completed process
    return proc
