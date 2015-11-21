#!/usr/bin/env python
# encoding: utf-8
import traceback
from tornado.gen import Return
from tornado.ioloop import IOLoop
from .base import BaseHandler


class RESTHandler(BaseHandler):
    REQUEST_TIMEOUT = 60
    REQUEST_MAX_SIZE = 2 ** 24  # 16Mb

    _BODYFULL_METHODS = {'PUT', 'POST'}
    _METHODS = ('get', 'post', 'put', 'delete', 'head')

    def __init__(self, application, request, **kwargs):
        super(RESTHandler, self).__init__(application, request, **kwargs)
        self.__json = self._NULL
        self.__headers_checked = False
        self.__headers_valid = True

        self.io_loop = IOLoop.current()

    def _check_headers(self):
        if self.request.method in self._BODYFULL_METHODS:
            return 'application/json' in self.request.headers.get('Content-Type', '')

        return True

    @property
    def json(self):
        if self.__json is self._NULL:
            self.__json = self._from_json(self.request.body)
        return self.__json

    def prepare(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        if not self._check_headers():
            return self.send_error(400)

        if self.request.method in self._BODYFULL_METHODS:
            self.__json = self._from_json(self.request.body)

    def write_error(self, status_code, **kwargs):
        self._auto_finish = False
        self.set_header("Content-Type", 'application/json; charset="utf-8"')

        error = {
            'error': {
                'code': status_code,
                'message': self._reason
            },

        }

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            error['traceback'] = list(str(line) for line in traceback.format_exception(*kwargs["exc_info"]))

        self.write(self._to_json(error))

    def response(self, data):
        self.finish(self._to_json(data))
