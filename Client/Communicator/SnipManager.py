import sys
from Communicator.LogicalClock import LogicalClock


class Snip:

    def __init__(self, msg, timestamp, sender):
        self.snip_msg = msg
        self.timestamp = timestamp
        self.sender = sender

class SnipManager:

    def __init__(self):
        self.clock = LogicalClock()
        self.__message_list = []

    # def sendUserMsg(self, msg):
    #     """ Sends a new user message to all connected peers (Thread safe)"""
    #     self.__message_list.append(msg)
    
    # def getUsersMsg(self):
    #     """ gets and waits for user input to console """
    #     # https: // stackoverflow.com/questions/70797/how-to-prompt-for-user-input-and-read-command-line-arguments
    #     self.__message_list.append('')

    def add(self, msg, timestamp, sender):
        """ Adds a new message to the list (Thread safe)"""
        self.clock.updateToValue(max(self.clock.getCounterValue(), int(timestamp)))
        snip = Snip(msg, timestamp, sender)
        self.__message_list.append(snip)
        self.clock.increment()
        self.print_msgs()

    def get_msgs(self):
        """ Get a list of all messages sent and recieved in order """
        return self.__message_list.copy()

    def print_msgs(self):
        print('\n\n')
        print('Timestamp:   |   Message:\n')
        for msg in self.__message_list:
            print('--------------------------\n')
            print(f'{msg.timestamp}     {msg.snip_msg}')
            print('--------------------------\n')
        print('\n\n')