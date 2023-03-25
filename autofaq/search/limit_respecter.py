import traceback
from enum import Enum, auto
from time import sleep, time
from typing import Callable
from uuid import uuid4


class State(Enum):
    QUEUED = auto()
    EXEC = auto()
    FAILED = auto()
    DONE = auto()


class LimitRespecter:
    def __init__(self, limits=None) -> None:
        self._reqs = {}
        self._queue = []
        self._done_times = []
        self._limits = limits

    def queue(self, task: Callable) -> str:
        _id = uuid4().hex
        self._reqs[_id] = {"task": task, "state": State.QUEUED}
        self._queue.append(_id)
        return _id

    def _exec(self, id):
        req = self._reqs[id]
        try:
            res = req["task"]()
            req["state"] = State.DONE
            req["result"] = res
            return res
        except Exception as e:
            req["state"] = State.FAILED
            req["err"] = {"exception": e, "trace": traceback.format_exc()}
            req["result"] = None
            self._done_times.append(time())
            return req["err"]

    def _window(self, window=60):
        start = time() - window
        return sum(map(lambda x: x >= start, self._done_times))

    def _available_for(self, window, limit):
        used = self._window(window=window)
        return limit - used

    def _available(self):
        if self._limits is None:
            # Arbitrary value proposing an available processing slot
            return 1
        n_limits = {
            window: self._available_for(window, limit)
            for window, limit in self._limits.items()
        }
        n_limits = list(sorted(n_limits.items(), key=lambda item: item[1]))
        min = n_limits[0][1]
        return min

    def _multi_tasks(self, n=1):
        m = min(n, len(self._queue))
        return [self._queue.pop(0) for _ in range(m)]

    def exec_all(self, callback=None):
        while len(self._queue) != 0:
            available = self._available()
            if available > 0:
                for t in self._multi_tasks(available):
                    self._reqs[t]["state"] = State.EXEC
                    r = self._exec(t)
                    if callback is not None:
                        callback(t, r)
            else:
                # TODO: Proper time extraction from _available
                sleep(1)
        results = dict(map(lambda k: (k[0], k[1]["result"]), list(self._reqs.items())))
        return results
