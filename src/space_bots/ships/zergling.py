"""Zergling: A Zergling ship in Space Bots"""

# Local Imports
from space_bots.ships import ship


class Zergling(ship.Ship):
    """Zergling: A Zergling ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='zergling', level=level)

        # Zergling specific stuff
        self.protect_asset = None
        self.p.incoming_damage_modifier = 0.75   # 25% reduction (they are slippery)
        self.p.collision_radius = 2.0  # Small collision radius helps avoid Torps

        # Zergling Level adjustments
        pass

        # Zerglings are 'frenzied'
        self.force_damp = 0.999

    def update(self):
        """Update the Zergling"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        self.general_target_movement(1.0)

        # Now actually call the move command (which uses force/mass calc)
        self.move()


# Simple test of the Zergling functionality
def test():
    """Test for Zergling Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.miner import Miner

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 700, 400)
    my_universe.add_asteroid(my_asteroid)

    # Create some Zerglings and a Miner Ship
    for _ in range(10):
        zerg_ship = Zergling(my_game_engine, 300, 300)
        my_universe.add_ship(zerg_ship, team='zerg')
    miner = Miner(my_game_engine, 400, 400)
    my_universe.add_ship(miner, team='earth')

    # Set mining asteroid
    class pos:
        pass
    pos.x = 500
    pos.y = 500
    miner.squad.protect(my_universe.battle_info.closest_asteroid(pos))

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
