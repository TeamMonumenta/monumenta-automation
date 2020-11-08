#!/usr/bin/env python3

# For interactive shell
import readline
import code

import os
import sys
import traceback

class BaseTest(object):
    def __init__(self, test_name, interact_on_fail=True):
        self.test_name = test_name
        self.interact_on_fail = interact_on_fail

        self.spacer = "╶"+"─"*78+"╴"

        self.error = None
        self.debug_error = None

    def test(self):
        """Run the test, raising an exception on error"""
        NotImplemented

    def debug(self):
        """Provide extra debug info on failure"""
        pass

    def run(self):
        """Run the test"""
        try:
            self.test()
        except Exception:
            self.error = traceback.format_exc()
        except KeyboardInterrupt:
            sys.exit()

        if self.error is not None:
            print("f: {}".format(self.test_name))
            if self.interact_on_fail:
                try:
                    self.debug()
                except Exception:
                    self.debug_error = traceback.format_exc()
                except KeyboardInterrupt:
                    sys.exit()
                self.interact()
        else:
            print("p: {}".format(self.test_name))

    def interact(self):
        """Display errors and interact on fail"""
        print(self.spacer)
        print("Traceback:")
        print(self.error)

        if self.debug_error is not None:
            print(self.spacer)
            print("Debug failed; debug traceback:")
            print(self.debug_error)

        print(self.spacer)
        print("self is the test case object.")
        variables = globals().copy()
        variables.update(locals())
        shell = code.InteractiveConsole(variables)
        shell.interact()
        print(self.spacer)

