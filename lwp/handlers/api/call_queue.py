#!/usr/bin/env python
# encoding: utf-8
import operator
from lwp.handlers.rest import RESTHandler
from lwp.handlers import call_queue


class CallQueue(RESTHandler):
    def get(self):
        self.response(
            list(
                sorted(call_queue.CallQueue.EVENTS.values(), key=operator.itemgetter('ts'), reverse=True)
            )
        )
