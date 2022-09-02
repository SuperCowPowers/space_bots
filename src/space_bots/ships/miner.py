"""Miner: A Miner ship in Space Bots"""

# Local Imports
from space_bots.utils import force_utils
from space_bots.ships import ship


class Miner(ship.Ship):
    """Miner: A Miner ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='miner')

        # Miner specific stuff
        self.mining_planet = None
        self.mining_yield = 0
        self.mining_announced = False

        # Mining level adjustments
        self.level = level
        self.p.laser_damage *= self.level

    def communicate(self, comms):
        """Communicate with Squad or Team"""
        if self.mining_yield > 10 and not self.mining_announced:
            comms.announce('mining_zenite', voice='male')
            self.mining_announced = True

        # Now let my super class do any communication
        super().communicate(comms)

    def update(self):
        """Update the Miner"""

        # General updates
        self.general_ship_updates()
        self.general_avoidance()

        # Get my closest Planet and go mine it
        self.mining_planet = self.squad.protection_asset
        if self.mining_planet:
            (_, _), (dx, dy) = force_utils.attraction_forces(self.mining_planet, self, self.p.laser_range-10)
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
        if self.mining_planet and force_utils.distance_between(self, self.mining_planet) < self.p.laser_range:
            self.game_engine.draw_line(self.p.color, (self.x, self.y), (self.mining_planet.x, self.mining_planet.y),
                                       width=self.p.laser_width)
            self.mining_yield += self.p.laser_damage


# Simple test of the Miner functionality
def test():
    """Test for Miner Class"""
    from space_bots import game_engine_adapter, planet
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Planet
    my_planet = planet.Planet(my_game_engine, 500, 500)
    my_universe.add_planet(my_planet)

    # Create a Miner ship
    miner_ship = Miner(my_game_engine, 400, 400)
    my_universe.add_ship(miner_ship, team='earth')

    # Set mining planet
    class pos:
        pass
    pos.x = 500
    pos.y = 500
    miner_ship.squad.protect(my_universe.battle_info.closest_planet(pos))

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
