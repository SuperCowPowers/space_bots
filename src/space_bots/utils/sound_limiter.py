"""Sound Limiter uses an internal memory cache to check if a sound has been played recently"""
import time


class SoundLimiter:
    """Sound Limiter uses a simple dictionary check to see if a sound has been played recently
       Usage:
            limiter = SoundLimiter()
            limiter.add(<sound_name>, <seconds>)
            limiter.is_limited(<sound_name>)
            limiter.clear()
    """
    def __init__(self):
        """SoundLimiter Initialization"""
        self._store = dict()

    def add_limit(self, sound_name, seconds):
        """Add a limit (x usage per second) for this sound name
            Args:
               sound_name: The name of the sound
               seconds: How many seconds the sound should be limited for (can be fractional)
        """
        expire = time.time() + seconds
        self._store[sound_name] = (expire, seconds)

    def is_limited(self, sound_name):
        """See if a sound is currently limited
           Args:
               sound_name: The name of the sound
           Returns:
               boolean: True or False
           Side Effects:
               If the return is 'False' then we update the sounds_name expiration
               with the assumption that the sound is going to be played right now
        """
        # Do we have a timer for this sound? If not add one with default 5 second limit
        if self._store.get(sound_name) is None:
            self.add_limit(sound_name, 5.0)
            return False

        # Now we test if the sound
        now = time.time()
        expire, seconds = self._store[sound_name]
        if now < expire:
            return True

        # If we're here the sound is past its limit
        # So store the sound name with a new expiration time
        self._store[sound_name] = (now + seconds, seconds)
        return False

    def clear(self):
        """Clear the cache"""
        self._store = dict()

    def dump(self):
        """Dump the cache (for debugging)"""
        for key, value in self._store.items():
            print(key, ':', value)


def test():
    """Test for the SoundLimiter class"""

    # Create the SoundLimiter
    limiter = SoundLimiter()
    limiter.add_limit('laser', 1)

    # Test storage
    assert limiter.is_limited('laser') is True

    # Test timeout
    time.sleep(1.1)
    assert limiter.is_limited('laser') is False

    # Dump the cache
    limiter.dump()


if __name__ == '__main__':

    # Run the test
    test()
