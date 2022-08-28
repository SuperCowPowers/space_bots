"""Tank: A Tank ship in Space Bots"""

# Local Imports
from space_bots.utils import force_utils
from space_bots.ships import ship


class Tank(ship.Ship):
    """Tank: A Tank ship in Space Bots"""
    def __init__(self, game_engine, x=100, y=100, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='tank')

        # Tank specific stuff
        self.protect_target = None
        self.p.damage_modifier = 0.75  # 25% reduction
        self.collision_radius = self.p.shield_radius * 2  # Tanks need their space
        self.shield_thrown = False

        # Tank Level adjustments
        self.level = level
        self.p.hp *= self.level
        self.s.hp = self.p.hp
        self.p.shield *= self.level
        self.s.shield = self.p.shield
        self.p.shield_recharge *= self.level
        self.p.hull_recharge *= self.level

    def update(self):
        """Update the Tank"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        # self.general_avoidance() Tanks don't avoid anyone :)

        # Tank specific stuff
        self.shield_thrown = False if not self.squad_in_combat() else self.shield_thrown

        # Move towards squads primary target (Tanks need to 'get in there')
        if self.squad.main_target:
            (dx, dy), (_, _) = force_utils.attraction_forces(self, self.squad.main_target, 0)
            self.force_x += dx * 2
            self.force_y += dy * 2

        # Track the lowest health TeamMate
        self.protect_target = self.battle_info.lowest_health_teammate(self)
        if not self.shield_thrown and self.protect_target.health_percent() < .1:
            print('Tank: Take the Pain!')
            self.announcer_messages.put('tank_cast_pain')
            self.protect_target.add_buff('take_the_pain')
            self.shield_thrown = True

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_laser()
        self.draw_ship()
        self.draw_shield()


# Simple test of the Tank functionality
def test():
    """Test for Tank Class"""
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
    my_planet = planet.Planet(my_game_engine, 500, 500)
    my_universe.add_planet(my_planet)

    # Create a Tank ship and a Healer Ship
    tank = Tank(my_game_engine, 300, 300)
    my_universe.add_ship(tank, team='earth')
    healer_ship = Healer(my_game_engine, 400, 400)
    my_universe.add_ship(healer_ship, team='earth')

    # Give the tank some damage to heal up
    tank.damage(800)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
