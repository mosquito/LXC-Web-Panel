#!/usr/bin/env python
# encoding: utf-8
import os
import container
from ..cacher import Cache
from .run import run
from . import BASE_PATH


@Cache(20)
def ls():
    '''
    List containers directory

    Note: Directory mode for Ubuntu 12/13 compatibility
    '''

    try:
        ct_list = filter(
            lambda x: all((
                os.path.isdir(os.path.join(BASE_PATH, x)),
                os.path.exists(os.path.join(BASE_PATH, x, 'config')))
            ),
            os.listdir(BASE_PATH)
        )
    except OSError:
        ct_list = []

    return sorted(ct_list)


def listx():
    '''
    List all containers with status (Running, Frozen or Stopped) in a dict
    Same as lxc-list or lxc-ls --fancy (0.9)
    '''

    stopped = []
    frozen = []
    running = []

    for container in ls():
        state = container.info(container)['state']
        if state == 'RUNNING':
            running.append(container)
        elif state == 'FROZEN':
            frozen.append(container)
        elif state == 'STOPPED':
            stopped.append(container)

    return {'RUNNING': running,
            'FROZEN': frozen,
            'STOPPED': stopped}


def running():
    return listx()['RUNNING']


def frozen():
    return listx()['FROZEN']


def stopped():
    return listx()['STOPPED']


@Cache(600)
def checkconfig():
    '''
    Returns the output of lxc-checkconfig (colors cleared)
    '''

    out = run('lxc-checkconfig', output=True)

    if out:
        return out.replace('[1;32m', '').replace('[1;33m', '') \
            .replace('[0;39m', '').replace('[1;32m', '') \
            .replace('\x1b', '').replace(': ', ':').split('\n')

    return out
