"""Comms: Class for managing communications in Space Bots"""
import queue
from collections import defaultdict

# Local imports
from space_bots.utils.sound_limiter import SoundLimiter


class Comms:
    """Comms: Class for managing communications in Space Bots"""

    def __init__(self):

        # The main functionality of this comms class is a defaultdict of Queues
        # Someone can post/pus to a new channel and then a SINGLE consumer can pick
        # up on the communications queue. Fancier 'broadcast' support/etc later
        self.channels = defaultdict(queue.SimpleQueue)

        # Limiter (yes we're using the sound limiter :)
        self.limiter = SoundLimiter()
        self.limiter.add_limit('display', 0.5)

    def get_messages(self, channel):
        """Get the next message on this channel"""
        while not self.channels[channel].empty():
            yield self.channels[channel].get()

    def put_message(self, channel, message):
        """Put a new message onto this channel"""
        self.channels[channel].put(message)

    def announce(self, voice_line, voice='random'):
        """Post a message to the announcements channel"""
        # Announcements have additional data sent with them
        info = {'voice': voice, 'voice_line': voice_line}
        self.put_message('announcements', info)

    def play_sound(self, sound_name):
        """Post a message to the announcements channel"""
        self.put_message('sounds', sound_name)

    def display(self, display_type, display_info):
        """Post a message to the display channel"""
        if not self.limiter.is_limited('display'):
            self.put_message('display', display_info)


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

    # Put out an announcement
    my_comms.announce('lets_rumble', 'male')
    for message in my_comms.get_messages('announcements'):
        print(message)


if __name__ == "__main__":
    test()
