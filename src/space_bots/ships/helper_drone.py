"""HelperDrone: A HelperDrone ship in Space Bots"""

# Local Imports
from space_bots import force_utils
from space_bots.ships import ship


class HelperDrone(ship.Ship):
    """HelperDrone: A HelperDrone ship in Space Bots"""
    def __init__(self, game_engine, x=100, y=100, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='helper_drone')

        # HelperDrone specific stuff
        self.protect_asset = None
        self.p.damage_modifier = 0.2  # 80% reduction (cause science)

        # HelperDrone Level adjustments
        self.level = level
        # Drones get a buff when there's more of them (real implementation TBD)
        self.p.laser_damage *= self.level*self.level  # Hee Hee

    def update(self):
        """Update the HelperDrone"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        # self.general_avoidance() HelperDrones are focused on protection target

        # Move towards protecting asset (HelperDrones need to protect the Asset)
        self.protect_asset = self.squad.protection_asset
        if self.protect_asset:
            (dx, dy), (_, _) = force_utils.attraction_forces(self, self.protect_asset, self.squad.protection_distance)
            self.force_x += dx * 10
            self.force_y += dy * 10

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_laser()
        self.draw_ship()
        self.draw_shield()


# Simple test of the HelperDrone functionality
def test():
    """Test for HelperDrone Class"""
    from space_bots import game_engine_adapter, planet, battle_state
    from space_bots.universe import Universe
    from space_bots.ships.miner import Miner

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Planet
    my_planet = planet.Planet(my_game_engine, 500, 500)
    my_universe.add_planet(my_planet)

    # Create a HelperDrone ship and a Miner Ship
    healer_ship = HelperDrone(my_game_engine, 300, 300)
    my_universe.add_ship(healer_ship)
    miner_ship = Miner(my_game_engine, 400, 400)
    my_universe.add_ship(miner_ship)

    # Give our ship the Battle State (universal in this case)
    my_battle_state = battle_state.BattleState(my_universe)
    healer_ship.set_battle_state(my_battle_state)
    miner_ship.set_battle_state(my_battle_state)

    # Give the miner some damage to heal up
    miner_ship.damage(300)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
