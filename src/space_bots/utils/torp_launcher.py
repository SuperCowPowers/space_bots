"""TorpLauncher: A Torpedo Launcher for Space Bots"""
import time
import math

# Local Imports
from space_bots.utils import weapon, force_utils, torp


class TorpLauncher(weapon.Weapon):
    """TorpLauncher: A Torpedo Launcher for Space Bots"""
    def __init__(self, ship, mount_points=8, level=1, min_capacitor=None):

        # Call SuperClass (Weapon) Initialization
        super().__init__(ship)

        # TorpLauncher specific stuff
        self.torps = []
        self.torp_range = 350
        self.next_torp_reload = 0
        self.current_time = None
        self.torp_cap_cost = 0.75
        self.max_torps = mount_points
        self.torp_level = level
        self.launch_points = self._generate_launch_points(mount_points)
        self.torp_reload_rate = 1.0/mount_points
        self.min_capacitor = min_capacitor if min_capacitor else self.torp_cap_cost * mount_points * 2

    def communicate(self, comms):
        """Weapons can post sounds and even announcements"""
        pass

    def update(self, target):
        """We need to manage both staged and launched Torps"""
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
                lp['torp'].x = lp['x'] + self.my_ship.x
                lp['torp'].y = lp['y'] + self.my_ship.y

        # Update All of my Torps (both staged and launched)
        for t in self.torps:
            t.update()

    def draw(self, target):
        """Draw All of my Torps (both staged and launched)"""
        for t in self.torps:
            t.draw()

    def fire(self, target):
        """Launch a Torpedo at the given Target"""

        # Is the target out of range?
        if target is None or force_utils.distance_between(self.my_ship, target) > self.torp_range:
            return

        # Only launch half if target at low health
        launch = self.max_torps  # FIXME: int(self.max_torps/2) if target.low_health() else self.max_torps

        # Fire Torps (by setting the active target)
        if self.fully_loaded():
            for lp in self.launch_points[:launch]:
                lp['torp'].set_target(target)
                lp['torp'].force_x = lp['x'] * .1
                lp['torp'].force_y = lp['y'] * .1
                lp['torp'].released = True
                lp['torp'] = None  # Torp released, so remove it from launch point

    def _generate_launch_points(self, n):
        """Internal: Generate N Launch Points Along the Circumference of the origin ship"""
        radius = self.my_ship.p.shield_radius
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
                new_torp = torp.Torp(self.my_ship, self.torp_level)
                lp['torp'] = new_torp
                self.torps.append(new_torp)  # We have to track torps even after they get released
                self.my_ship.s.capacitor -= self.torp_cap_cost
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

    def torp_available_for_loading(self):
        """Is a new Torp available for firing?"""
        return (self.my_ship.s.capacitor > self.min_capacitor) and \
               (self.current_time > self.next_torp_reload) and \
               (len(self.torps) < self.max_torps)


# Simple test of the TorpLauncher functionality
def test():
    """Test for TorpLauncher Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.ship import Ship
    from space_bots.ships.tank import Tank
    from space_bots.ships.healer import Healer

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 600, 300)
    my_universe.add_asteroid(my_asteroid)

    # Create a Tank, healer, and fire some Torps
    tank = Tank(my_game_engine, 300, 600)
    my_universe.add_ship(tank, team='earth')
    healer_ship = Healer(my_game_engine, 400, 400, level=2)
    my_universe.add_ship(healer_ship, team='earth')

    zerg = Ship(my_game_engine, 900, 600, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')
    zerg = Ship(my_game_engine, 900, 600, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
