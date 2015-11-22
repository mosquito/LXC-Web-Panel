# encoding: utf-8
from tornado.gen import coroutine
from ...lxc.container import config
from ..base import threaded
from ..rest import RESTHandler


class Container(RESTHandler):
    config = staticmethod(threaded(config))

    @coroutine
    def get(self, name):
        self.response((yield self.config(name)))
