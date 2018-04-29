#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import time

class timings():
    def __init__(self,enabled=True):
        self.enabled = enabled
        #self.timeFunction = time.clock
        self.timeFunction = time.time
        if self.enabled:
            self.start = self.timeFunction()
            self.last = self.start

    def nextStep(self,msg="Unnamed step."):
        if self.enabled:
            timeNow = self.timeFunction()
            timeTotal = self._formatTime(timeNow - self.start)
            timeDelta = self._formatTime(timeNow - self.last)
            self.last = timeNow
            print "[{}, {}] {}".format(timeTotal,timeDelta,msg)

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

