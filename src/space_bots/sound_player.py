"""SoundPlayer: Class for Managing/Playing Sound/Music in Space Bots"""
from os import walk, path
from random import choice
import queue

import pygame

# Local Imports
from space_bots.utils.sound_limiter import SoundLimiter


class SoundPlayer:
    """SoundPlayer: Class for Managing/Playing Sound/Music in Space Bots"""
    def __init__(self):

        # Set up our sound limiter (avoids spamming sounds too close together)
        self.sound_limiter = SoundLimiter()
        self.sound_queue = queue.Queue()
        self.mixer = pygame.mixer

        # Loading the default background music
        music_location = path.join(path.dirname(__file__), 'sounds/background_music/')
        self.music_tracks = {}
        for music_file in next(walk(music_location), (None, None, []))[2]:
            file_tag = path.splitext(music_file)[0]
            self.music_tracks[file_tag] = path.join(music_location, music_file)

        # Randomly pick one
        self.current_background_track = choice(list(self.music_tracks.keys()))
        self.mixer.music.load(self.music_tracks[self.current_background_track])
        self.mixer.music.set_volume(0.3)  # Background should be a bit lower volume

        # Load up our sound files
        sound_location = path.join(path.dirname(__file__), 'sounds/interactive_sounds/')
        self.sound_clips = {}
        for sound_file in next(walk(sound_location), (None, None, []))[2]:
            clip_tag = path.splitext(sound_file)[0]
            self.sound_clips[clip_tag] = self.mixer.Sound(path.join(sound_location, sound_file))
            self.sound_clips[clip_tag].set_volume(0.3)

        # Load up our voice-over files
        sound_location = path.join(path.dirname(__file__), 'sounds/voice_overs/')
        for sound_file in next(walk(sound_location), (None, None, []))[2]:
            # Ignore
            if sound_file == '.DS_Store':
                continue
            clip_tag = path.splitext(sound_file)[0]
            self.sound_clips[clip_tag] = self.mixer.Sound(path.join(sound_location, sound_file))
            self.sound_clips[clip_tag].set_volume(1.0)

        # FIXME: Hardcoded limits for now
        self.sound_limiter.add_limit('laser', 0.01)
        self.sound_limiter.add_limit('explosion', 1)

    def play_background_music(self, mix='default'):
        """Play some Background Music"""
        self.mixer.music.play(-1)

    def stop_background(self):
        """Stop the Background Music"""
        self.mixer.music.stop()

    def add_sound_to_queue(self, sound_name, busy_wait=False):
        """Play a particular sound clip"""
        # Note: This queues the sound and calls the internal play sound

        # Do we actually have this sound?
        if sound_name not in self.sound_clips:
            print(f'Sound: {sound_name} not found...')
            return

        # Check the limiter
        if self.sound_limiter.is_limited(sound_name):
            return

        # Add this sound to the queue
        self.sound_queue.put((sound_name, busy_wait))

    def play_queue(self):
        """Internal: Okay now we pull sounds from the queue and actually play them"""

        """Play the next sound on the queue"""
        while not self.sound_queue.empty():
            # Let's check the busy wait for the next item on the queue (without popping)
            next_sound, busy_wait = self.sound_queue.queue[0]
            if busy_wait and self.mixer.get_busy():
                return

            # Grab next sound off queue and play it
            next_sound, busy_wait = self.sound_queue.get()
            self.sound_clips[next_sound].play()

    def announce(self, voice_line, announcer='random'):
        """Have the announcer say stuff"""

        # This just constructs a voice_line tag
        choices = ['male', 'female']
        announcer = choice(choices) if announcer == 'random' else announcer
        voice_line_name = f'{voice_line}_{announcer}'

        # Play the voice line (with chosen announcer)
        self.add_sound_to_queue(voice_line_name, busy_wait=True)


# Simple test of the SoundPlayer functionality
def test():
    """Test for SoundPlayer Class"""
    from time import sleep

    # Initialize PyGame (the Universe does this for the real game)
    pygame.init()

    # Create a Sound Adapter class and test some stuff out
    my_sound = SoundPlayer()

    # We should only here one laser due to limiter
    sleep(1)
    my_sound.add_sound_to_queue('laser')
    my_sound.play_queue()
    print('Need to wait for limit...')
    sleep(0.6)
    my_sound.add_sound_to_queue('laser')
    my_sound.play_queue()
    my_sound.add_sound_to_queue('laser')  # Should NOT hear this one (spam)
    my_sound.play_queue()
    print('Need to wait for limit...')
    sleep(2)
    my_sound.add_sound_to_queue('explosion')
    my_sound.play_queue()

    # What if we simultaneously play stuff?
    sleep(3)
    my_sound.add_sound_to_queue('laser')
    my_sound.add_sound_to_queue('explosion')
    my_sound.play_queue()

    # Announce
    my_sound.announce('lets_rumble', 'male')
    my_sound.announce('great_match', 'female')
    for _ in range(100):
        sleep(0.1)
        my_sound.play_queue()

    # Background
    my_sound.play_background_music()
    sleep(5)
    my_sound.stop_background()


if __name__ == "__main__":
    test()
