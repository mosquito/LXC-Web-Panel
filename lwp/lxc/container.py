#!/usr/bin/env python
# encoding: utf-8
from object_cacher import ObjectCacher

from .exceptions import (
    ContainerAlreadyExists,
    ContainerDoesntExists,
    ContainerAlreadyRunning,
    ContainerNotRunning
)

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

    command = 'lxc-create -n {}'.format(container)
    command += ' -t {}'.format(template)

    if storage:
        command += ' -B {}'.format(storage)

    if xargs:
        command += ' -- {}'.format(xargs)

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

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

        try:
            ObjectCacher.invalidate("lxc.info")
            ObjectCacher.invalidate("lxc.list")
        except KeyError as e:
            log.error(e)

        return run(command)


def info(container):
    '''
    Check info from lxc-info
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exist!'.format(container))

    output = run('lxc-info -qn {}|grep -i "State\|PID\|IP"'.format(container),
                 output=True)

    params = {"state": None, "pid": None}
    if output:
        for i in output.splitlines():
            n, v = i.split()
            n = n.strip(":").lower()
            params[n] = v

    try:
        params['pid'] = int(params['pid'])
    except:
        pass

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

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

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

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

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

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

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

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

    return run('lxc-unfreeze -n {}'.format(container))


def destroy(container):
    '''
    Destroys a container
    '''

    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exists!'.format(container))

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

    return run('lxc-destroy -n {}'.format(container))


def cgroup(container, key, value):
    if not exists(container):
        raise ContainerDoesntExists(
            'Container {} does not exist!'.format(container))

    try:
        ObjectCacher.invalidate("lxc.info")
        ObjectCacher.invalidate("lxc.list")
    except KeyError as e:
        log.error(e)

    return run('lxc-cgroup -n {} {} {}'.format(container, key, value))
