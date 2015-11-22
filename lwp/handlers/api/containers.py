#!/usr/bin/env python
# encoding: utf-8
from tornado.gen import coroutine
from ..base import threaded
from ..rest import RESTHandler
from lwp.lxc.container import ls
from ...lxc.container import info


class Containers(RESTHandler):
    @coroutine
    def get(self):
        self.response((yield [self.info(i) for i in (yield self.list())]))

    @threaded
    def list(self):
        return ls()

    @threaded
    def info(self, name):
        ret = info(name)
        ret['name'] = name
        return ret
