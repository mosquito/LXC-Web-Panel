#!/usr/bin/env python
# encoding: utf-8
from tornado.gen import coroutine
from ..base import threaded
from ..rest import RESTHandler
from ...lxc.system import ls


class Containers(RESTHandler):
    @coroutine
    def get(self):
        self.response((yield self.list()))

    @threaded
    def list(self):
        return ls()
