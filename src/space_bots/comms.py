"""Comms: Class for managing communications in Space Bots"""
import queue
from collections import defaultdict


class Comms:
    """Comms: Class for managing communications in Space Bots"""

    def __init__(self):

        # The main functionality of this comms class is a defaultdict of Queues
        # Someone can post/pus to a new channel and then a SINGLE consumer can pick
        # up on the communications queue. Fancier 'broadcast' support/etc later
        self.channels = defaultdict(queue.SimpleQueue)

    def get_messages(self, channel):
        """Get the next message on this channel"""
        while not self.channels[channel].empty():
            yield self.channels[channel].get()

    def put_message(self, channel, message):
        """Put a new message onto this channel"""
        self.channels[channel].put(message)


# Simple test of the Comms functionality
def test():
    """Test for communications Class for space bots"""

    # Create the class and run some tests
    my_comms = Comms()

    # Add some messages to the universe channel
    my_comms.put_message('universe', 'hi from the future')
    my_comms.put_message('universe', '1')
    my_comms.put_message('universe', '2')

    # Grab my messages
    for message in my_comms.get_messages('universe'):
        print(message)
    for message in my_comms.get_messages('universe'):
        print(message)

    # Put some message for two different squads
    my_comms.put_message('squad:roughnecks', 'jo momma')
    my_comms.put_message('squad:smellys', 'his momma')

    # Grab a squad message
    for message in my_comms.get_messages('squad:smellys'):
        print(message)

    # Put and get a 'data' message
    my_comms.put_message('announcer', {'voice': 'male', 'message': "lets_rumble"})
    for message in my_comms.get_messages('announcer'):
        print(message)


if __name__ == "__main__":
    test()
