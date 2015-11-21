#!/usr/bin/env python
# encoding: utf-8

class ContainerAlreadyExists(Exception):
    pass


class ContainerDoesntExists(Exception):
    pass


class ContainerAlreadyRunning(Exception):
    pass


class ContainerNotRunning(Exception):
    pass