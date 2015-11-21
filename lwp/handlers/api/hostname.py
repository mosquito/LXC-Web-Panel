#!/usr/bin/env python
# encoding: utf-8
import socket
from ..rest import RESTHandler


class Hostname(RESTHandler):
    def get(self):
        self.response({'hostname': socket.gethostname()})
