from contextlib import contextmanager
import time
from typing import Optional

class Timer:
    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
        self.elapsed: float = 0

    @contextmanager
    def track(self):
        self.start_time = time.perf_counter()
        try:
            yield self
        finally:
            self.end_time = time.perf_counter()
            self.elapsed = self.end_time - self.start_time
