import sys

class SnipManager:

    def __init__(self):
        self.__message_list = []

    # def sendUserMsg(self, msg):
    #     """ Sends a new user message to all connected peers (Thread safe)"""
    #     self.__message_list.append(msg)
    
    # def getUsersMsg(self):
    #     """ gets and waits for user input to console """
    #     # https: // stackoverflow.com/questions/70797/how-to-prompt-for-user-input-and-read-command-line-arguments
    #     self.__message_list.append('')

    def add(self, msg):
        """ Adds a new message to the list (Thread safe)"""
        self.__message_list.append(msg)

    def get_msgs(self):
        """ Get a list of all messages sent and recieved in order """
        return self.__message_list.copy()
