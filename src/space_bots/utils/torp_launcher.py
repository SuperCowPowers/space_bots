"""TorpLauncher: A Torpedo Launcher for Space Bots"""
import time
import random

# Local Imports
from space_bots.utils import force_utils, torp


class TorpLauncher:
    """TorpLauncher: A Torpedo Launcher for Space Bots"""
    def __init__(self, ship, max_torps=8, level=1):

        # TorpLauncher specific stuff
        self.origin_ship = ship
        self.max_torps = max_torps
        self.torps = []
        self.torp_level = level
        self.torp_range = 300
        self.torp_reload_rate = 0.0
        self.next_torp_reload = 0
        self.current_time = None

    def expire_torps(self):
        """Time Expiration for Existing Torps"""
        for t in self.torps:
            if t.release_counter > t.expire:
                t.delete_me = True

    def update(self):
        """Update Existing Torps"""

        # Delete expired or exploded torps
        self.current_time = time.time()
        self.expire_torps()
        self.torps = [t for t in self.torps if not t.delete_me]

        # Update existing Torps
        for t in self.torps:
            t.update()

    def torp_available(self):
        """Is a new Torp available for firing?"""
        return (self.origin_ship.s.capacitor > 1) and \
               (self.current_time > self.next_torp_reload) and \
               (len(self.torps) < self.max_torps)

    def fire(self, target):
        """Launch a Torpedo at the given Target"""

        # Do we have a target and is it within range?
        if target is None or not force_utils.distance_between(self.origin_ship, target) < self.torp_range:
            return

        # Fire new Torps
        if self.torp_available():
            # Create the Torp and randomize its Launch
            t = torp.Torp(self.origin_ship, target, self.torp_level)
            t.force_x = random.uniform(-3, 3)
            t.force_y = random.uniform(-3, 3)
            self.torps.append(t)
            self.next_torp_reload = self.current_time + self.torp_reload_rate
            self.origin_ship.s.capacitor -= 1


# Simple test of the TorpLauncher functionality
def test():
    """Test for TorpLauncher Class"""
    from space_bots import game_engine_adapter, planet
    from space_bots.universe import Universe
    from space_bots.ships.ship import Ship
    from space_bots.ships.tank import Tank

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Planet
    my_planet = planet.Planet(my_game_engine, 600, 300)
    my_universe.add_planet(my_planet)

    # Create a Tank and fire some Torps
    tank = Tank(my_game_engine, 300, 600)
    my_universe.add_ship(tank, team='earth')

    zerg = Ship(my_game_engine, 900, 600, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
