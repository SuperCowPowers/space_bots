"""Healer: A Healer ship in Space Bots"""

# Local Imports
from space_bots import force_utils
from space_bots.ships import ship


class Healer(ship.Ship):
    """Healer: A Healer ship in Space Bots"""
    def __init__(self, game_engine, x=100, y=100):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='healer')

        # Healer specific stuff
        self.healing_target = None

    def communicate(self):
        """Communicate with Squad or Team"""
        pass

    def update(self):
        """Update the Healer"""

        # General updates
        self.general_ship_updates()

        # Avoidance of Adversaries
        # FIXME: This needs to take into account ship damage
        adversaries = self.squad.adversaries if self.squad else []
        for other_ship in adversaries:
            (dx, dy), (_, _) = force_utils.repulsion_forces(self, other_ship, rest_distance=self.p.keep_range)
            self.force_x += dx
            self.force_y += dy

        # Get the lowest health TeamMate and move towards them
        self.healing_target = self.battle_state.lowest_health_teammate(self)
        if self.healing_target and self.healing_target != self:
            # Rush
            rush = 3 if self.healing_target.health_percent() < .5 else 1
            (_, _), (dx, dy) = force_utils.attraction_forces(self.healing_target, self, self.p.laser_range - 10)
            self.force_x += dx * rush
            self.force_y += dy * rush

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_healing_laser()
        self.draw_ship()
        self.draw_shield()

    def draw_ship(self):
        """Draw the Healer Icon"""
        hull_health = min(self.s.hp / self.p.hp + 0.6, 1.0)
        hull_color = (self.p.color[0] * hull_health, self.p.color[1] * hull_health, self.p.color[2] * hull_health)
        self.game_engine.draw_circle((30, 30, 30), (self.x, self.y), self.p.radius, width=0)
        self.game_engine.draw_circle(hull_color, (self.x, self.y), self.p.radius, width=self.p.ship_width)
        if self.low_health():
            self.game_engine.draw_circle((200, 200, 0), (self.x, self.y), 3)
        if self.critical_health():
            self.game_engine.draw_circle((240, 0, 0), (self.x, self.y), 3)

    def draw_healing_laser(self):
        """Draw the mining lasers"""
        if self.healing_target and force_utils.distance_between(self, self.healing_target) < self.p.laser_range:

            # Does my target need healing
            if self.healing_target.health_percent() < .95:
                self.game_engine.draw_line(self.p.color, (self.x, self.y), (self.healing_target.x, self.healing_target.y),
                                           width=self.p.laser_width)

                # Out of combat heal buff
                healing_power = 10 if not self.squad_in_combat() else 1
                self.healing_target.heal(self.p.laser_damage * healing_power)


# Simple test of the Healer functionality
def test():
    """Test for Healer Class"""
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

    # Create a Healer ship and a Miner Ship
    healer_ship = Healer(my_game_engine, 300, 300)
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