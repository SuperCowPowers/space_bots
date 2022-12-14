"""BattleState: Class stores all the battle state (ship, asteroids, etc) for Space Bots"""

# Local imports
from space_bots.utils import force_utils


class BattleState:
    """"BattleState: Class stores all the battle state (ship, asteroids, etc) for Space Bots"""
    def __init__(self, universe, scanner_range):

        # Set my attributes
        self.universe = universe
        self.scanner_range = scanner_range

    def all_ships(self):
        """Ask the battle state for ALL the ships"""
        return self.universe.all_ships

    def zerg_ships(self):
        return [s for s in self.universe.all_ships if s.team == 'zerg']

    def adversary_ships(self, ship):
        """Ask the battle state for ships NOT on my team within the specified range"""
        adversaries = [s for s in self.universe.all_ships if s.team != ship.team]
        return [s for s in adversaries if force_utils.distance_between(ship, s) < self.scanner_range]

    def team_ships(self, ship):
        """Ask the battle state for all ships on my team"""
        return [s for s in self.universe.all_ships if s.team == ship.team]

    def all_asteroids(self):
        """Ask the battle state for ALL the asteroids"""
        return self.universe.asteroids

    def lowest_health_teammate(self, ship):
        if not self.all_ships():
            return None
        ship_health = [(s, s.health_percent()) for s in self.team_ships(ship)]
        ship_health.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_health][0]


# Simple test of the BattleState functionality
def test():
    """Test for BattleState Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe
    from space_bots import asteroid
    from space_bots.ships import ship

    # Create a universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create our BattleState
    BattleState(my_universe)

    # Create some Asteroids
    for _ in range(5):
        my_asteroid = asteroid.Asteroid(my_game_engine, 500, 500)
        my_universe.add_asteroid(my_asteroid)

    # Create some ships
    for _ in range(8):
        my_universe.add_ship(ship.Ship(my_game_engine, 200, 200))

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
