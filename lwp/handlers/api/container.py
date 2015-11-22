# encoding: utf-8
from tornado.gen import coroutine
from tornado.web import HTTPError

from ...lxc.container import config, write_config
from ..base import threaded
from ..rest import RESTHandler


class Container(RESTHandler):
    config = staticmethod(threaded(config))
    write_config = staticmethod(threaded(write_config))

    @coroutine
    def get(self, name):
        self.response((yield self.config(name)))

    @coroutine
    def put(self, name):
        if 'config' not in self.json:
            raise HTTPError(400)

        yield self.write_config(name, self.json['config'])