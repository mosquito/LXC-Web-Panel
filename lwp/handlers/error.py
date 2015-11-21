#!/usr/bin/env python
# encoding: utf-8
from .rest import RESTHandler


class NotFoundError(RESTHandler):
    def prepare(self):
        self.send_error(404)
