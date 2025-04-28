# app/utils/logger.py

import time

class SimpleLogger:
    def __init__(self):
        self.start_times = {}

    def start(self, step: str):
        print(f"➡️ Start: {step}")
        self.start_times[step] = time.time()

    def end(self, step: str):
        duration = time.time() - self.start_times.get(step, time.time())
        print(f"✅ End: {step} (took {duration:.2f} seconds)")
