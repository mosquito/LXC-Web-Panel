#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime
from threading import RLock

import os

from .exceptions import (
    ContainerAlreadyExists,
    ContainerDoesntExists,
    ContainerAlreadyRunning,
    ContainerNotRunning
)

from ..cacher import Cache
from .run import run
from . import log, BASE_PATH
from lwp import __version__


def exists(container):
    '''
    Check if container exists
    '''

    if container in ls():
        return True

    return False


def create(container, template='ubuntu', storage=None, xargs=None):
    '''
    Create a container (without all options)
    Default template: Ubuntu
    '''

    if exists(container):
        raise ContainerAlreadyExists(
            'Container {} already created!'.format(container))

    command = ['lxc-create', '-n', container, '-t', template]

    if storage:
        command.append('-B')
        command.append(storage)

    if xargs:
        command.append('--')
        command.append(xargs)

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run(command)


def clone(orig=None, new=None, snapshot=False):
    '''
    Clone a container (without all options)
    '''

    if orig and new:
        if exists(new):
            raise ContainerAlreadyExists(
                'Container {} already exist!'.format(new))

        command = 'lxc-clone -o {} -n {}'.format(orig, new)
        if snapshot:
            command += ' -s'

        Cache.invalidate("lxc.info")
        Cache.invalidate("lxc.list")

        return run(command)


def config(container):
    path = os.path.join(BASE_PATH, container, 'config')
    if not os.path.exists(path):
        raise ContainerDoesntExists(container)

    with open(path) as cfg:
        return list(
            map(
                lambda x: tuple(
                    map(
                        lambda i: i.strip(),
                        x.split('=')
                    )
                ),
                filter(
                    lambda x: x.strip() and not x.strip().startswith("#"),
                    cfg
                )
            )
        )


_CONFIG_WRITE_LOCK = RLock()


def write_config(container, config_list):
    path = os.path.join(BASE_PATH, container, 'config')
    if not os.path.exists(path):
        raise ContainerDoesntExists(container)

    with _CONFIG_WRITE_LOCK:
        with open(path, 'w+') as cfg:
            cfg.write("# Generated by LXC Web panel ver: {0}\n".format(__version__))
            cfg.write("# {0}\n".format(str(datetime.now())))

            for key, value in config_list:
                cfg.write("{0} = {1}\n".format(key, value))


@Cache(600, oid='lxc.info')
def info(container):
    '''
    Check info from lxc-info
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exist!'.format(container))

    info = map(
        lambda x: map(lambda s: s.strip(':'), x.lower().split()),
        filter(
            lambda x: any(x.lower().startswith(p) for p in ('state', 'pid', 'ip')),
            run(['lxc-info', '-qn', container], output=True).splitlines()
        )
    )

    params = {"state": None, "pid": None, "ip": []}
    for key, value in info:
        if key in params and params[key]:
            params[key] = [params[key]]
            params[key].append(value)
        else:
            params[key] = value

    params['pid'] = int(params['pid']) if params['pid'] and params['pid'].isdigits() else params['pid']
    return params


def start(container):
    '''
    Starts a container
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exists!'.format(container))

    if container in running():
        raise ContainerAlreadyRunning(
            'Container {} is already running!'.format(container))

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run(['lxc-start', '-dn', container])


def stop(container):
    '''
    Stops a container
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exists!'.format(container))

    if container in stopped():
        raise ContainerNotRunning(
            'Container {} is not running!'.format(container))

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run('lxc-stop -n {}'.format(container))


def freeze(container):
    '''
    Freezes a container
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exists!'.format(container))

    if not container in running():
        raise ContainerNotRunning(
            'Container {} is not running!'.format(container))

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run('lxc-freeze -n {}'.format(container))


def unfreeze(container):
    '''
    Unfreezes a container
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exists!'.format(container))

    if not container in frozen():
        raise ContainerNotRunning(
            'Container {} is not frozen!'.format(container))

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run('lxc-unfreeze -n {}'.format(container))


def destroy(container):
    '''
    Destroys a container
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exists!'.format(container))

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run('lxc-destroy -n {}'.format(container))


def cgroup(container, key, value):
    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exist!'.format(container))

    Cache.invalidate("lxc.info")
    Cache.invalidate("lxc.list")

    return run('lxc-cgroup -n {} {} {}'.format(container, key, value))


@Cache(20, oid='lxc.list')
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

    for item in ls():
        state = info(item)['state']
        if state == 'RUNNING':
            running.append(item)
        elif state == 'FROZEN':
            frozen.append(item)
        elif state == 'STOPPED':
            stopped.append(item)

    return {
        'RUNNING': running,
        'FROZEN': frozen,
        'STOPPED': stopped
    }


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


@Cache(86400)
def lsb_release():
    try:
        _, out = map(lambda x: x.strip(), run(['lsb_release', '-d'], output=True).split(":"))
    except Exception as e:
        out = "Linux %s" % run(['uname', '-r'], output=True).strip()

    return out