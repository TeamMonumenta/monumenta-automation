import time

class Timings():
    def __init__(self,enabled=True):
        self.enabled = enabled
        self.time_function = time.time
        if self.enabled:
            self.start = self.time_function()
            self.last = self.start

    def nextStep(self,msg="Unnamed step."):
        if self.enabled:
            time_now = self.time_function()
            time_total = self._formatTime(time_now - self.start)
            time_delta = self._formatTime(time_now - self.last)
            self.last = time_now
            print(f'[{time_total}, {time_delta}] {msg}')

    def _formatTime(self,seconds):
        h = int(seconds/3600)
        m = int(seconds/60)%60
        s = seconds%60
        if h>0:
            return f'{h:0>2}:{m:0>2}:{s:06.3f}'
        elif m>0:
            return f'   {m:0>2}:{s:06.3f}'
        else:
            return f'      {s:06.3f}'

