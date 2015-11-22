# encoding: utf-8
import logging
from functools import wraps
from time import time

from multiprocessing import RLock

FunctionType = type(lambda:None)

log = logging.getLogger("lwp.cache")


class Result(object):
    __slots__ = ['ts', 'result']

    def __init__(self, result):
        self.ts = time()
        self.result = result


class Cache(object):
    __slots__ = ('timeout', 'ignore_self', 'oid')

    CACHE = {}

    def __init__(self, timeout, ignore_self=False, oid=None):
        self.timeout = timeout
        self.ignore_self = ignore_self
        self.oid = oid

    @staticmethod
    def hash_func(key):
        if isinstance(key, FunctionType):
            return ".".join((key.__module__, key.__name__))
        else:
            return str(key)

    @classmethod
    def invalidate(cls, func):
        fkey = cls.hash_func(func)

        for key in list(cls.CACHE):
            if hash(key[0]) == hash(fkey):
                cls.CACHE.pop(key)

    def __call__(self, func):
        key = self.oid or self.hash_func(func)

        @wraps(func)
        def wrap(*args, **kwargs):
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

                if (ret.ts + self.timeout) < time():
                    self.CACHE.pop(args_key)
                    log.debug("EXPIRED Cache [%s] %r", key, args_key)

                if ret:
                    log.debug("HIT Cache [%s] %r", key, args_key)
                    return ret.result

            ret = Result(func(*args, **kwargs))
            self.CACHE[args_key] = ret

            log.debug("MISS Cache [%s] %r", key, args_key)
            return ret.result

        return wrap
