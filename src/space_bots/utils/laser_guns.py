"""LaserGuns: Ship Laser Guns for Space Bots"""
import math

# Local Imports
from space_bots.utils import force_utils


class LaserGuns:
    """LaserGuns: Ship Laser Guns for Space Bots"""
    def __init__(self, ship):

        # LaserGuns specific stuff
        self.origin_ship = ship
        self.range = self.origin_ship.p.laser_range
        self.width = self.origin_ship.p.laser_width
        self.cap_cost = 0.05
        self.needs_recharge = False
        self.full_charge = 400
        self.current_charge = 0
        self.color = self.origin_ship.p.color

        # These vars are defined in set_configuration
        self.single_mount = True
        self.mount_points = None
        self.laser_level = None
        self.min_capacitor = None
        self.game_engine = None

    def set_deployment(self, mount_points=2):
        """Set the deployment of the Torp Launcher"""
        self.single_mount = True if mount_points == 1 else False
        self.mount_points = mount_points
        self.cap_cost *= mount_points
        self.min_capacitor = self.cap_cost
        self.game_engine = self.origin_ship.game_engine

    def is_deployed(self):
        return self.mount_points is not None

    def draw_mount(self, coords):
        self.game_engine.draw_circle(self.color, coords, 3, width=0)
        self.game_engine.draw_circle((220, 220, 220), coords, 4, width=1)

    def draw_fire(self, target):
        """Since they share a lot of logic, combine Draw and Fire"""

        # Some ships do not have LaserGuns
        if not self.is_deployed():
            return

        # Do we have enough capacitor?
        if self.origin_ship.s.capacitor < self.min_capacitor:
            self.current_charge = 0
            self.needs_recharge = True
            return

        # Does our laser need a recharge
        if self.needs_recharge:
            self.current_charge += 1
            self.needs_recharge = False if self.current_charge >= self.full_charge else True
            return

        # Is the target out of range?
        if target is None or force_utils.distance_between(self.origin_ship, target) > self.range:
            return

        # Get our current laser damage from origin ship (might be buffed)
        laser_damage = self.origin_ship.p.laser_damage * self.mount_points

        # Draw (and Fire) the lasers
        if self.single_mount:
            self.game_engine.draw_line(self.color, (self.origin_ship.x, self.origin_ship.y),
                                       (target.x, target.y), width=self.width)
        else:
            # Assuming 2 mounts for now
            # FIXME: Seems overly complicated
            theta = force_utils.get_angle(self.origin_ship, target) + math.pi/2
            radius = self.origin_ship.p.shield_radius
            first_mount = (radius * math.cos(theta), radius * math.sin(theta))
            second_mount = (-first_mount[0], -first_mount[1])
            first_mount = (first_mount[0] + self.origin_ship.x, first_mount[1] + self.origin_ship.y)
            second_mount = (second_mount[0] + self.origin_ship.x, second_mount[1] + self.origin_ship.y)
            self.game_engine.draw_line(self.color, (first_mount[0], first_mount[1]),
                                       (target.x, target.y), width=self.width)
            self.game_engine.draw_line(self.color, (second_mount[0], second_mount[1]),
                                       (target.x, target.y), width=self.width)

        # Fire the laser(s) and do damage to target ship
        target.damage(laser_damage)
        self.origin_ship.damage_done += laser_damage
        self.origin_ship.s.capacitor -= self.cap_cost


# Simple test of the LaserGuns functionality
def test():
    """Test for LaserGuns Class"""
    from space_bots import game_engine_adapter, planet
    from space_bots.universe import Universe
    from space_bots.ships.ship import Ship
    from space_bots.ships.fighter import Fighter

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Planet
    my_planet = planet.Planet(my_game_engine, 600, 300)
    my_universe.add_planet(my_planet)

    # Create a Fighter and fire some Lasers
    tank = Fighter(my_game_engine, 300, 600)
    my_universe.add_ship(tank, team='earth')

    zerg = Ship(my_game_engine, 900, 600, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
