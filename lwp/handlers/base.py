#!/usr/bin/env python
# encoding: utf-8
import ujson
from functools import wraps

import datetime

from tornado.web import RequestHandler

try:
    import cPickle as pickle
except ImportError:
    import pickle


class BaseHandler(RequestHandler):
    _NULL = object()
    THREAD_POOL = None

    @property
    def thread_pool(self):
        return self.THREAD_POOL

    @classmethod
    def threaded(cls, func):
        @wraps(func)
        def wrap(*args, **kwargs):
            return cls.THREAD_POOL.submit(func, *args, **kwargs)

        return wrap

    @staticmethod
    def _to_json(data):
        return ujson.dumps(data)

    @staticmethod
    def _from_json(data):
        return ujson.loads(data)

    def get_secure_cookie(self, name, value=None, max_age_days=31, min_version=None):
        val = super(BaseHandler, self).get_secure_cookie(
            name, value, max_age_days=max_age_days, min_version=min_version
        )

        return pickle.loads(val) if val else val

    def set_secure_cookie(self, name, value, expires_days=30, version=None, **kwargs):
        return super(BaseHandler, self).set_secure_cookie(
            name, pickle.dumps(value), expires_days=expires_days,
            version=version, **kwargs
        )


threaded = BaseHandler.threaded


class cache(object):
    def __init__(self, timeout, use_expires=False, expire_timeout=60):
        self.timeout = timeout
        self.expire_timeout = expire_timeout
        self.use_expires = use_expires

    def __call__(self, func):
        @wraps(func)
        def wrap(handler, *args, **kwargs):
            ret = func(handler, *args, **kwargs)
            self.set_cache(handler)
            return ret

        return wrap

    def set_cache(self, handler, **kwargs):
        if hasattr(handler, '_new_cookie') and handler._new_cookie:
            return

        if handler._status_code == 200:
            if handler.request.method == "GET" and kwargs.get('timeout', self.timeout):
                handler.set_header("X-Accel-Expires", kwargs.get('timeout', self.timeout))

            if kwargs.get('use_expires', self.use_expires):
                handler.set_header(
                    "Expires",
                    (datetime.datetime.now() + datetime.timedelta(
                        seconds=kwargs.get('expire_timeout', self.expire_timeout)
                    )).strftime("%a, %d %b %Y %H:%M:%S %Z")
                )
                handler.set_header(
                    "Cache-Control",
                    "max-age={0}".format(kwargs.get('expire_timeout', self.expire_timeout))
                )
