#!/usr/bin/env python
# encoding: utf-8
import os
from tornado.gen import coroutine
from time import sleep
from ...cacher import Cache
from ...lxc import BASE_PATH
from ...lxc.system import lsb_release
from ..base import threaded
from ..rest import RESTHandler


class HostInfo(RESTHandler):
    @coroutine
    def get(self):
        ret = {}
        (
            ret['memory'],
            ret['disk'],
            ret['cpu'],
            ret['uptime'],
            ret['release']
        ) = yield [
            self.memory(),
            self.disk_usage(),
            self.host_cpu_percent(),
            self.uptime(),
            self.distro_name(),
        ]

        self.response(ret)

    @staticmethod
    @threaded
    @Cache(86400)
    def distro_name():
        return lsb_release()

    @staticmethod
    @threaded
    @Cache(1)
    def host_cpu_percent():
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

    @threaded
    @Cache(1, ignore_self=True)
    def uptime(self):
        with open('/proc/uptime') as f:
            uptime = float(f.readline().split()[0])

            days, hours, minutes, seconds = (
                uptime // 86400, uptime % 86400 // 3600,
                uptime % 86400 % 3600 // 60,
                uptime % 86400 % 3600 % 60
            )

            return {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
            }

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
