#!/usr/bin/env python
# encoding: utf-8
import time
from tornado.concurrent import Future
from tornado.gen import maybe_future, coroutine
from tornado.ioloop import IOLoop
from uuid import uuid4
from base64 import b32encode


class CallQueue(object):
    EVENTS = {}

    @classmethod
    def get_task_id(cls):
        return b32encode(uuid4().bytes).lower()

    @classmethod
    def put(cls, name, func, *args, **kwargs):
        task_id = cls.get_task_id()
        io_loop = IOLoop.current()

        future = Future()

        @coroutine
        def inner():
            try:
                result = yield maybe_future(func(*args, **kwargs))
                future.set_result(result)
                cls.EVENTS[task_id]['state'] = True
            except Exception as e:
                future.set_exception(e)
                cls.EVENTS[task_id]['state'] = False
            finally:
                cls.EVENTS[task_id]['resolved'] = int(io_loop.time() * 1000)
                io_loop.call_later(60, lambda: cls.EVENTS.pop(task_id))

        io_loop.add_callback(inner)
        cls.EVENTS[task_id] = {
            'name': name,
            'state': None,
            'ts': int(io_loop.time() * 1000),
            'resolved': None,
        }

        future.task_id = task_id

        return future

    @classmethod
    def task_info(cls, task_id):
        return cls.EVENTS.get(task_id, -1)
