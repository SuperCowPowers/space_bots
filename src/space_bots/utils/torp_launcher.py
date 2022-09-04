"""TorpLauncher: A Torpedo Launcher for Space Bots"""
import time
import math

# Local Imports
from space_bots.utils import force_utils, torp


class TorpLauncher:
    """TorpLauncher: A Torpedo Launcher for Space Bots"""
    def __init__(self, ship):

        # TorpLauncher specific stuff
        self.origin_ship = ship
        self.torps = []
        self.torp_range = 250
        self.torp_reload_rate = 0.1
        self.next_torp_reload = 0
        self.current_time = None
        self.min_capacitor = 1

        # These vars are defined in set_configuration
        self.torp_level = None
        self.max_torps = None
        self.launch_points = None

    def set_deployment(self, launch_points, level=1):
        """Set the deployment of the Torp Launcher"""
        self.max_torps = launch_points
        self.torp_level = level
        self.launch_points = self._generate_launch_points(launch_points)

    def is_deployed(self):
        return self.launch_points is not None

    def _generate_launch_points(self, n):
        """Internal: Generate N Launch Points Along the Circumference of the origin ship"""
        radius = self.origin_ship.p.shield_radius
        theta_list = [2.0*math.pi*i/n for i in range(n)]
        hard_points = [(radius * math.cos(t), radius * math.sin(t)) for t in theta_list]
        launch_points = [{'torp': None, 'x': h[0], 'y': h[1]} for h in hard_points]
        return launch_points

    def first_available_launch_point(self, new_torp):
        # Update next reload
        self.next_torp_reload = self.current_time + self.torp_reload_rate

        # Select the next launch
        for lp in self.launch_points:
            if lp['torp'] is None:
                lp['torp'] = new_torp
                self.origin_ship.s.capacitor -= 1
                return

        # Shouldn't get here
        print('No Launch Points!!!!')

    def expire_torps(self):
        """Time Expiration for Existing Torps"""
        for t in self.torps:
            if t.release_counter > t.expire:
                t.delete_me = True

    def update(self):
        """Update Existing Torps"""

        # Many ships do not have a TorpLauncher
        if not self.is_deployed():
            return

        # Delete expired or exploded torps
        self.current_time = time.time()
        self.expire_torps()
        self.torps = [t for t in self.torps if not t.delete_me]

        # Load Torps into our launch points
        if self.torp_available():
            t = torp.Torp(self.origin_ship, self.torp_level)
            self.torps.append(t)
            self.first_available_launch_point(t)

        # Update launch points relative to ship movements
        for lp in self.launch_points:
            if lp['torp']:
                lp['torp'].x = lp['x'] + self.origin_ship.x
                lp['torp'].y = lp['y'] + self.origin_ship.y

        # Update already launched Torps
        for t in self.torps:
            t.update()

    def torp_available(self):
        """Is a new Torp available for firing?"""
        return (self.origin_ship.s.capacitor > self.min_capacitor) and \
               (self.current_time > self.next_torp_reload) and \
               (len(self.torps) < self.max_torps)

    def fire(self, target):
        """Launch a Torpedo at the given Target"""

        # Do we have a target and is it within range?
        if target is None or not force_utils.distance_between(self.origin_ship, target) < self.torp_range:
            return

        # Fire Torps (by setting the active target)
        if len(self.torps) == self.max_torps:
            for lp in self.launch_points:
                if lp['torp']:
                    lp['torp'].set_target(target)
                    lp['torp'].force_x = lp['x'] * .1
                    lp['torp'].force_y = lp['y'] * .1
                    lp['torp'].released = True
                    lp['torp'] = None  # Torp is now free, so remove it from launch point


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
