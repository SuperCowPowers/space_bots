"""Fighter: A Fighter ship in Space Bots"""

# Local Imports
from space_bots.ships import ship


class Fighter(ship.Ship):
    """Fighter: A Fighter ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='fighter')

        # Fighter specific stuff
        self.self_buffs = ['first_strike']

        # Fighter Level adjustments
        self.level = level
        self.p.laser_damage *= self.level


# Simple test of the Fighter functionality
def test():
    """Test for Fighter Class"""
    from space_bots import game_engine_adapter, planet
    from space_bots.universe import Universe
    from space_bots.ships.healer import Healer

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Planet
    my_planet = planet.Planet(my_game_engine, 700, 400)
    my_universe.add_planet(my_planet)

    # Create a Fighter ship and a Healer Ship
    fighter_ship = Fighter(my_game_engine, 300, 300)
    my_universe.add_ship(fighter_ship, team='earth')
    healer_ship = Healer(my_game_engine, 400, 400)
    my_universe.add_ship(healer_ship, team='earth')

    # Give the miner some damage to heal up
    fighter_ship.damage(300)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
