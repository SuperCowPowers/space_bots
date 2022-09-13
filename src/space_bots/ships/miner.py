"""Miner: A Miner ship in Space Bots"""

# Local Imports
from space_bots.utils import weapon, laser_guns, force_utils
from space_bots.ships import ship


class Miner(ship.Ship):
    """Miner: A Miner ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='miner', level=level)

        # Miner specific stuff
        self.mining_asteroid = None
        self.mining_yield = 0
        self.mining_announced = False
        self.report_depleted = False

        # Mining level adjustments
        pass

        # Weapons
        self.laser_guns = laser_guns.LaserGuns(self, mount_points=2)  # Mining Lasers :)
        self.torp_launcher = weapon.NoWeapon(self)

    def communicate(self, comms):
        """Communicate with Squad or Team"""
        if self.mining_yield > 1 and not self.mining_announced:
            comms.announce('mining_zenite', voice='male')
            self.mining_announced = True
        """
        if self.report_depleted:
            comms.announce('minerals_depleted')
            self.report_depleted = False
        """

        # Now let my super class do any communication
        super().communicate(comms)

    def update(self):
        """Update the Miner"""

        # General updates
        self.general_ship_updates()
        self.general_avoidance(passive=3.0)  # Miner needs to avoid enemies

        # Mining laser update
        self.laser_guns.update(self.mining_asteroid)

        # If we don't have a current mining asteroid, find one
        if self.mining_asteroid is None:
            new_asteroid = self.squad.best_asteroid(self)
            self.squad.protect(new_asteroid)
            self.mining_asteroid = self.squad.protection_asset

        # Move toward the mining asteroid
        if self.mining_asteroid:
            (_, _), (dx, dy) = force_utils.attraction_forces(self.mining_asteroid, self, self.p.laser_range/5)
            self.force_x += dx
            self.force_y += dy

        # Let Squad know my Zenite Yield
        self.squad.total_zenite += self.mining_yield

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_mining_laser()
        super().draw()

    def draw_mining_laser(self):
        """Draw the mining lasers"""
        self.laser_guns.draw(self.mining_asteroid)
        if self.mining_asteroid and force_utils.distance_between(self, self.mining_asteroid) < self.p.laser_range:
            self.laser_guns.fire(self.mining_asteroid)

            # Extract the minerals
            extracted = self.mining_asteroid.extract_minerals(self.p.laser_damage)
            self.mining_yield += extracted

            # Report if asteroid depleted
            if extracted == 0:
                self.report_depleted = True
                self.mining_asteroid = None


# Simple test of the Miner functionality
def test():
    """Test for Miner Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 600, 500)
    my_universe.add_asteroid(my_asteroid)

    # Create a Miner ship
    miner_ship = Miner(my_game_engine, 400, 400)
    my_universe.add_ship(miner_ship, team='earth')

    # Set mining asteroid
    class pos:
        pass
    pos.x = 500
    pos.y = 500
    miner_ship.squad.protect(my_universe.battle_info.closest_asteroid(pos))

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
