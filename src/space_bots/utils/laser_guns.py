"""LaserGuns: Ship Laser Guns for Space Bots"""

# Local Imports
from space_bots.utils import weapon, force_utils
from space_bots.utils.mounts import CenterMount, GimbalMount


class LaserGuns(weapon.Weapon):
    """LaserGuns: Ship Laser Guns for Space Bots"""
    def __init__(self, ship, mount_points=1):

        # Call SuperClass (Weapon) Initialization
        super().__init__(ship)

        # LaserGuns specific stuff
        self.range = self.my_ship.p.laser_range
        self.width = self.my_ship.p.laser_width
        self.cap_cost = 0.05
        self.needs_recharge = False
        self.full_charge = 400
        self.current_charge = 0
        self.mount = CenterMount(ship) if mount_points == 1 else GimbalMount(ship, mount_points)
        self.cap_cost *= mount_points
        self.min_capacitor = self.cap_cost

    def communicate(self, comms):
        """Weapons can post sounds and even announcements"""
        pass

    def update(self, target):
        """Weapons update themselves, for instance Torp Launchers need to update Torps"""
        self.mount.update(target)

    def draw(self, target):
        """Draw the Laser Mounts"""
        self.mount.draw()

    def fire(self, target):
        """Fire the Weapon at the given target
           Note: Some Weapons (e.g. Lasers) will draw themselves when they are fired
        """
        # Do we have enough capacitor?
        if self.my_ship.s.capacitor < self.min_capacitor:
            self.current_charge = 0
            self.needs_recharge = True
            return

        # Does our laser need a recharge
        if self.needs_recharge:
            self.current_charge += 1
            self.needs_recharge = False if self.current_charge >= self.full_charge else True
            return

        # Is the target out of range?
        if target is None or force_utils.distance_between(self.my_ship, target) > self.range:
            return

        # Get our current laser damage from my ship (might be buffed)
        laser_damage = self.my_ship.p.laser_damage * self.mount.num_mount_points() * self.my_ship.p.outgoing_damage_modifier

        # Fire (and Draw) the lasers
        for mount_point in self.mount.get_mount_locations():
            self.game_engine.draw_line(self.color, (mount_point[0], mount_point[1]), (target.x, target.y), width=self.width)

        # Fire the laser(s) and do damage to target ship
        target.damage(laser_damage)
        self.my_ship.damage_done += laser_damage
        self.my_ship.s.capacitor -= self.cap_cost


# Simple test of the LaserGuns functionality
def test():
    """Test for LaserGuns Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.ship import Ship
    from space_bots.ships.fighter import Fighter

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 600, 300)
    my_universe.add_asteroid(my_asteroid)

    # Create a Fighter and fire some Lasers
    tank = Fighter(my_game_engine, 300, 600)
    my_universe.add_ship(tank, team='earth')

    zerg = Ship(my_game_engine, 900, 600, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
