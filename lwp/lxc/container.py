#!/usr/bin/env python
# encoding: utf-8
from .exceptions import (
    ContainerAlreadyExists,
    ContainerDoesntExists,
    ContainerAlreadyRunning,
    ContainerNotRunning
)
from ..cacher import Cache
from .system import ls, running, frozen, stopped
from .run import run
from . import log


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

    return run('lxc-start -dn {}'.format(container))


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
