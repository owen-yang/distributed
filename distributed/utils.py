from __future__ import print_function, division, absolute_import

import socket

from tornado import gen

def get_ip():
    return [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close())
        for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


from contextlib import contextmanager

@contextmanager
def ignoring(*exceptions):
    try:
        yield
    except exceptions:
        pass


@gen.coroutine
def ignore_exceptions(coroutines, *exceptions):
    """ Process list of coroutines, ignoring certain exceptions

    >>> coroutines = [cor(...) for ...]  # doctest: +SKIP
    >>> x = yield ignore_exceptions(coroutines, TypeError)  # doctest: +SKIP
    """
    wait_iterator = gen.WaitIterator(*coroutines)
    results = []
    while not wait_iterator.done():
        with ignoring(*exceptions):
            result = yield wait_iterator.next()
            results.append(result)
    raise gen.Return(results)


@gen.coroutine
def All(*args):
    """ Wait on many tasks at the same time

    Err once any of the tasks err.

    See https://github.com/tornadoweb/tornado/issues/1546
    """
    if len(args) == 1 and isinstance(args[0], list):
        args = args[0]
    tasks = gen.WaitIterator(*args)
    results = []
    while not tasks.done():
        result = yield tasks.next()
        results.append(result)
    raise gen.Return(results)