#!/usr/bin/env python
# encoding: utf-8
import os
from tornado.gen import coroutine, Return
from time import sleep
from ...cacher import Cache
from ...lxc import BASE_PATH
from ..base import threaded
from ..rest import RESTHandler


class HostInfo(RESTHandler):
    @coroutine
    def get(self):
        ret = {}
        (
            ret['memory'], ret['disk'],
            ret['cpu']
        ) = yield [
            self.memory(),
            self.disk_usage(),
            self.host_cpu_percent()
        ]
        self.response(ret)

    @threaded
    @Cache(1, ignore_self=True)
    def host_cpu_percent(self):
        def cpu_stat_percent():
            with open('/proc/stat', 'r') as f:
                stat = f.readline()

                data = map(float, stat.split()[1:4])
                idle = data[-1]
                total = sum(data)

            return idle, total

        def get_info():
            first_idle, first_total = cpu_stat_percent()

            sleep(0.05)

            second_idle, second_total = cpu_stat_percent()

            total = second_total - first_total
            percent = 1. - (total - (second_idle - first_idle)) / total if total else 0

            return percent * 100

        data = [get_info() for _ in range(8)]
        return reduce(lambda x, y: x + y / float(len(data)), data, 0)

    @threaded
    @Cache(10, ignore_self=True)
    def disk_usage(self):
        st = os.statvfs(BASE_PATH)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize

        return {'total': total, 'used': used, 'free': free}

    @staticmethod
    @threaded
    @Cache(600)
    def memory():
        def unhumanize(value):
            value, coeff = value.split()
            coeff_map = {
                'b': 1,
                'kb': 1024,
                'mb': 1024 ** 2,
                'gb': 1024 ** 3,
                'tb': 1024 ** 4,
            }
            return float(value) * coeff_map.get(coeff, 1)

        with open('/proc/meminfo') as mem_info:
            return dict(
                map(
                    lambda x: (x[0], unhumanize(x[1])),
                    filter(
                        lambda x: x[0] in set(('memtotal', 'cached', 'memfree', 'buffers')),
                        map(
                            lambda line: map(
                                lambda x: x.strip().strip(":").lower(), line.split(None, 1)
                            ),
                            mem_info
                        )
                    )
                )
            )
