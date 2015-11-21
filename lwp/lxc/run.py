#!/usr/bin/env python
# encoding: utf-8
import shlex
import subprocess


def run(cmd, output=False):
    if isinstance(cmd, basestring):
        cmd = shlex.split(str(cmd))

    if output:
        try:
            out = subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError:
            out = False

        return out

    try:
        subprocess.check_call(cmd, universal_newlines=True)  # returns 0 for True
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode
