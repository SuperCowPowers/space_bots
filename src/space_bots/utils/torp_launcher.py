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
        self.torp_range = 300
        self.next_torp_reload = 0
        self.current_time = None
        self.torp_cap_cost = 1.0

        # These vars are defined in set_configuration
        self.launch_points = None
        self.torp_level = None
        self.max_torps = None
        self.torp_reload_rate = None
        self.min_capacitor = None

    def set_deployment(self, launch_points, level=1):
        """Set the deployment of the Torp Launcher"""
        self.max_torps = launch_points
        self.torp_level = level
        self.launch_points = self._generate_launch_points(launch_points)
        self.torp_reload_rate = 1.0/launch_points
        self.min_capacitor = self.torp_cap_cost * launch_points

    def is_deployed(self):
        return self.launch_points is not None

    def _generate_launch_points(self, n):
        """Internal: Generate N Launch Points Along the Circumference of the origin ship"""
        radius = self.origin_ship.p.shield_radius
        theta_list = [2.0*math.pi*i/n for i in range(n)]
        hard_points = [(radius * math.cos(t), radius * math.sin(t)) for t in theta_list]
        launch_points = [{'torp': None, 'x': h[0], 'y': h[1]} for h in hard_points]
        return launch_points

    def load_next_available_launch_point(self):
        # Update next reload
        self.next_torp_reload = self.current_time + self.torp_reload_rate

        # Select the next launch point
        for lp in self.launch_points:
            if lp['torp'] is None:
                new_torp = torp.Torp(self.origin_ship, self.torp_level)
                lp['torp'] = new_torp
                self.torps.append(new_torp)  # We have to track torps even after they get released
                self.origin_ship.s.capacitor -= self.torp_cap_cost
                return

        # Shouldn't get here
        print('No Launch Points!!!!')

    def live_torps(self):
        """Return a list of Torps that have been launched"""
        return [t for t in self.torps if t.released]

    def fully_loaded(self):
        """Is the Launcher fully Loaded?"""
        return all([lp['torp'] for lp in self.launch_points])

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
        if self.torp_available_for_loading():
            self.load_next_available_launch_point()

        # Update launch points relative to ship movements
        for lp in self.launch_points:
            if lp['torp']:
                lp['torp'].x = lp['x'] + self.origin_ship.x
                lp['torp'].y = lp['y'] + self.origin_ship.y

        # Update already launched Torps
        for t in self.torps:
            t.update()

    def torp_available_for_loading(self):
        """Is a new Torp available for firing?"""
        return (self.origin_ship.s.capacitor > self.min_capacitor) and \
               (self.current_time > self.next_torp_reload) and \
               (len(self.torps) < self.max_torps)

    def fire(self, target):
        """Launch a Torpedo at the given Target"""

        # Many ships do not have a TorpLauncher
        if not self.is_deployed():
            return

        # Is the target out of range?
        if target is None or force_utils.distance_between(self.origin_ship, target) > self.torp_range:
            return

        # Fire Torps (by setting the active target)
        if self.fully_loaded():
            for lp in self.launch_points:
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
