import sys
from Communicator.LogicalClock import LogicalClock
from datetime import datetime

class Snip:
    """ Used to maintain snip instances and snip information """

    def __init__(self, msg, timestamp, sender):
        self.snip_msg = msg
        self.timestamp = timestamp
        self.sender = sender
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Ack:
    def __init__(self, peer, timestamp):
        self.timestamp = timestamp
        self.peer = peer

class SnipManager:
    """ Manages snips from and to our process """

    def __init__(self):
        self.clock = LogicalClock()
        self.__message_list = []
        self.__ack_list = []

    def add(self, msg, timestamp, sender):
        """ Adds a new snip message to the list (Thread safe), updates logical clock and displays snip messages """
        self.clock.updateToValue(max(self.clock.getCounterValue(), int(timestamp)))
        snip = Snip(msg, timestamp, sender)
        self.__message_list.append(snip)
        self.clock.increment()
        self.print_msgs()

    def add_ack(self, peer, timestamp):
        ack = Ack(peer, timestamp)
        self.__ack_list.append(ack)

    def get_msgs(self):
        """ Get a list of all messages sent and recieved in order """
        snippets = self.__message_list.copy()
        snippets.sort(reverse=False, key =lambda x: int(x.timestamp))
        return snippets

    def get_acks(self):
        acks = self.__ack_list.copy()
        return acks

    def addCtchSnip(self, originalSender, timestamp, content):
        """ Checks is recieved snip message is a duplicate before adding to list of snips """
        for snip in self.__message_list:
            if snip.sender == originalSender and snip.timestamp == timestamp:
                return
        self.add(content, timestamp, originalSender)

    def print_msgs(self):
        """ Formats and prints snip messages """
        messages = self.get_msgs()
        print(messages)
        print('\n\n')
        print('Timestamp:   |   Message:\n')
        for msg in messages:
            print('--------------------------\n')
            print(f'{msg.timestamp}             {msg.snip_msg}')
            print('--------------------------\n')
        print('\n\n')
