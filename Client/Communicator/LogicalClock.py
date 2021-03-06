import sys


class LogicalClock:
    """ Used to maintain logical clock """

    def __init__(self):
        self.counter = 0

    def increment(self):
        """ Increments Logical Clock by one"""
        self.counter = self.counter + 1

    def updateToValue(self, val):
        """ Update Logical Clocks counter to specific value """
        self.counter = val

    def getCounterValue(self):
        """ Get the logical clocks ounter value """
        return self.counter
