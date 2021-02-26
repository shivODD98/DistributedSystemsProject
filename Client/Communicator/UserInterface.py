import sys

class UserInterface:

    def __init__(self):
        self.__message_list = []
        self.__peers = []

    def updatePeers(self, peers):
        """ Updates list of peers """
        self.__peers = peers


    def sendUserMsg(self, msg):
        """ Sends a new user message to all connected peers (Thread safe)"""
        self.__message_list.append(msg)
    
    def getUsersMsg(self):
        """ gets and waits for user input to console """
        self.__message_list.append('')

    def add(self, msg):
        """ Adds a new message to the list (Thread safe)"""
        self.__message_list.append(msg)

    def get_msgs(self):
        """ Get a list of all messages sent and recieved in order """
        return self.__message_list.copy()
