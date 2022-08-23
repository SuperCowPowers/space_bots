"""Miner: A Miner ship in Space Bots"""

# Local Imports
from space_bots import force_utils
from space_bots.ships import ship


class Miner(ship.Ship):
    """Miner: A Miner ship in Space Bots"""
    def __init__(self, game_engine, x=100, y=100):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='miner')

        # Miner specific stuff
        self.mining_planet = None
        self.collision_radius = self.p.shield_radius * 2  # Miners need their space
        # self.mining_hardpoint_offsets = [(self.p.radius, 0), (0, 0), (0, self.p.radius)]

    def communicate(self):
        """Communicate with Squad or Team"""
        pass

    def update(self):
        """Update the Miner"""

        # General updates
        self.general_ship_updates()
        self.general_avoidance()

        # Get my closest Planet and go mine it
        # FIXME self.mining_planet = self.battle_state.closest_planet(self)
        self.mining_planet = self.squad.protection_asset
        if self.mining_planet:
            (_, _), (dx, dy) = force_utils.attraction_forces(self.mining_planet, self, self.p.laser_range-10)
            self.force_x += dx * 2
            self.force_y += dy * 2

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_mining_laser()
        self.draw_ship()
        self.draw_shield()

    def draw_ship(self):
        """Draw the Miner Icon"""
        hull_health = min(self.s.hp / self.p.hp + 0.6, 1.0)
        hull_color = (self.p.color[0] * hull_health, self.p.color[1] * hull_health, self.p.color[2] * hull_health)
        self.game_engine.draw_circle((30, 30, 30), (self.x, self.y), self.p.radius, width=0)
        self.game_engine.draw_circle(hull_color, (self.x, self.y), self.p.radius, width=self.p.ship_width)
        if self.low_health():
            self.game_engine.draw_circle((200, 200, 0), (self.x, self.y), 5, width=0)
        if self.critical_health():
            self.game_engine.draw_circle((240, 0, 0), (self.x, self.y), 5, width=0)

    def draw_mining_laser(self):
        """Draw the mining lasers"""
        if self.mining_planet and force_utils.distance_between(self, self.mining_planet) < self.p.laser_range:
            self.game_engine.draw_line(self.p.color, (self.x, self.y), (self.mining_planet.x, self.mining_planet.y),
                                       width=self.p.laser_width)


# Simple test of the Miner functionality
def test():
    """Test for Miner Class"""
    from space_bots import game_engine_adapter, planet, battle_state
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
    my_universe.add_ship(miner_ship)

    # Give our ship the Battle State (universal in this case)
    my_battle_state = battle_state.BattleState(my_universe)
    miner_ship.set_battle_state(my_battle_state)

    # Give the ship a push and do some damage
    miner_ship.force_x = 1000
    miner_ship.force_y = -200
    miner_ship.damage(100)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
