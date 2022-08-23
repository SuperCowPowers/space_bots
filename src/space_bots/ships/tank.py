"""Tank: A Tank ship in Space Bots"""

# Local Imports
from space_bots import force_utils
from space_bots.ships import ship


class Tank(ship.Ship):
    """Tank: A Tank ship in Space Bots"""
    def __init__(self, game_engine, x=100, y=100):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='tank')

        # Tank specific stuff
        self.protect_target = None
        self.p.damage_modifier = 0.80  # 20% reduction
        self.collision_radius = self.p.shield_radius * 3  # Tanks need space
        self.shield_thrown = False

    def communicate(self):
        """Communicate with Squad or Team"""
        pass

    def update(self):
        """Update the Tank"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        # self.general_avoidance() Tanks don't avoid anyone :)

        # Tank specific stuff
        self.shield_thrown = False if not self.squad_in_combat() else self.shield_thrown

        # Track the lowest health TeamMate
        self.protect_target = self.battle_state.lowest_health_teammate(self)
        if not self.shield_thrown and self.protect_target.health_percent() < .1:
            print('Tank: Take the Pain!')
            self.protect_target.s.shield = self.protect_target.p.shield
            self.shield_thrown = True

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_laser()
        self.draw_ship()
        self.draw_shield()

    def draw_ship(self):
        """Draw the Tank Icon"""
        hull_health = min(self.s.hp / self.p.hp + 0.6, 1.0)
        hull_color = (self.p.color[0] * hull_health, self.p.color[1] * hull_health, self.p.color[2] * hull_health)
        self.game_engine.draw_circle((30, 30, 30), (self.x, self.y), self.p.radius, width=0)
        self.game_engine.draw_circle(hull_color, (self.x, self.y), self.p.radius, width=self.p.ship_width)
        if self.low_health():
            self.game_engine.draw_circle((200, 200, 0), (self.x, self.y), 6, width=0)
        if self.critical_health():
            self.game_engine.draw_circle((240, 0, 0), (self.x, self.y), 6, width=0)

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


# Simple test of the Tank functionality
def test():
    """Test for Tank Class"""
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

    # Create a Tank ship and a Miner Ship
    healer_ship = Tank(my_game_engine, 300, 300)
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
