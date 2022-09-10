"""Drone: A Drone ship in Space Bots"""

# Local Imports
from space_bots.utils import force_utils
from space_bots.ships import ship


class Drone(ship.Ship):
    """Drone: A Drone ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='drone')

        # Drone specific stuff
        self.protect_asset = None
        self.p.damage_modifier = 0.5  # 50% reduction (reflection science)

        # Drone Level adjustments
        self.level = level
        self.p.laser_damage *= self.level*self.level  # Hee Hee

    def update(self):
        """Update the Drone"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        self.general_avoidance()
        self.general_target_movement(aggressive=0.5)

        # Move towards protecting asset (Drones need to protect the Asset)
        self.protect_asset = self.squad.protection_asset
        if self.protect_asset:
            (dx, dy), (_, _) = force_utils.attraction_forces(self, self.protect_asset, self.squad.protection_distance)
            self.force_x += dx * 3
            self.force_y += dy * 3

        # Now actually call the move command (which uses force/mass calc)
        self.move()


# Simple test of the Drone functionality
def test():
    """Test for Drone Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.healer import Healer

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 500, 500)
    my_universe.add_asteroid(my_asteroid)

    # Create a Drone ship and a Miner Ship
    drone = Drone(my_game_engine, 400, 450)
    my_universe.add_ship(drone, team='earth')
    healer_ship = Healer(my_game_engine, 400, 400)
    my_universe.add_ship(healer_ship, team='earth')

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
