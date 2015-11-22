# encoding: utf-8
from tornado.gen import coroutine
from tornado.web import HTTPError
from lwp.lxc import container
from lwp.handlers.base import threaded
from lwp.handlers.rest import RESTHandler
from lwp.handlers.call_queue import CallQueue


class Actions(object):
    write_config = staticmethod(threaded(container.write_config))
    config = staticmethod(threaded(container.config))
    start = staticmethod(threaded(container.start))
    stop = staticmethod(threaded(container.stop))
    freeze = staticmethod(threaded(container.freeze))
    destroy = staticmethod(threaded(container.destroy))
    clone = staticmethod(threaded(container.clone))

    __actions__ = set(['stop', 'start', 'clone', 'delete', 'freeze'])


class Container(RESTHandler):
    @coroutine
    def get(self, name):
        self.response((yield Actions.config(name)))

    @coroutine
    def put(self, name):
        if 'config' not in self.json:
            raise HTTPError(400)

        yield Actions.write_config(name, self.json['config'])

    @coroutine
    def post(self, name):

        if 'action' not in self.json and self.json['action'] not in Actions.__actions__:
            raise HTTPError(400)

        yield CallQueue.put(
            'Performing action "{0}" for container "{1}"'.format(self.json['action'], name),
            getattr(Actions, self.json['action']),
            name
        )
