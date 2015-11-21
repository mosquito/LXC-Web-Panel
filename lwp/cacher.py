# encoding: utf-8
import logging
from functools import wraps
from time import time

from multiprocessing import RLock

log = logging.getLogger("lwp.cache")


class Result(object):
    __slots__ = ['ts', 'result']

    def __init__(self, result):
        self.ts = time()
        self.result = result


class Cache(object):
    __slots__ = ('timeout', 'ignore_self')

    CACHE = {}
    LOCK = RLock()

    def __init__(self, timeout, ignore_self=False):
        self.timeout = timeout
        self.ignore_self = ignore_self

    def hash_func(self, func):
        return ".".join((func.__module__, func.__name__))

    def __call__(self, func):
        key = self.hash_func(func)

        @wraps(func)
        def wrap(*args, **kwargs):
            with self.LOCK:
                args_key = tuple(
                    map(
                        hash,
                        (
                            key,
                            tuple(map(hash, args[1:] if self.ignore_self else args)),
                            tuple(map(lambda x: tuple(map, x), kwargs.items()))
                        )
                    )
                )

                if args_key in self.CACHE:
                    ret = self.CACHE[args_key]

                    if (ret.ts + self.timeout) > time():
                        self.CACHE.pop(args_key)

                    if ret:
                        log.debug("HIT Cache [%s] %r", key, args_key)
                        return ret.result

                ret = Result(func(*args, **kwargs))
                self.CACHE[args_key] = ret

                log.debug("MISS Cache [%s] %r", key, args_key)
                return ret.result

        return wrap
