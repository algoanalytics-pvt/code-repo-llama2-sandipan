import time

class Timer:
    def __init__(self, logger):
        self.logger = logger
        self._start_time = None

    def start(self):
        """Start a new timer"""
        try:
            if self._start_time is not None:
                raise Exception

            self._start_time = time.perf_counter()
        except Exception as e:
            self.logger.info(msg=f"Timer is running. Use .stop() to stop it")
        
    def stop(self, methodName: str):
        """Stop the timer, and report the elapsed time"""
        try:
            self.methodName = methodName
            if self._start_time is None:
                raise Exception

            elapsed_time = time.perf_counter() - self._start_time
            self._start_time = None
            self.logger.info(msg=f"Elapsed time for {self.methodName}: {elapsed_time:0.4f} seconds")
        except Exception as e:
            self.logger.info(msg=f"Timer is not running. Use .start() to start it")