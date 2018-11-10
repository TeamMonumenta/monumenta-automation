#!/usr/bin/env python3
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
            print( "[{}, {}] {}".format(time_total,time_delta,msg) )

    def _formatTime(self,seconds):
        h = int(seconds/3600)
        m = int(seconds/60)%60
        s = seconds%60
        if h>0:
            return "{:0>2}:{:0>2}:{:06.3f}".format(h,m,s)
        elif m>0:
            return "   {:0>2}:{:06.3f}".format(m,s)
        else:
            return "      {:06.3f}".format(s)

