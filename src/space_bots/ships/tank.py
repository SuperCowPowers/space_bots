"""Tank: A Tank ship in Space Bots"""
import time

# Local Imports
from space_bots.utils import force_utils
from space_bots.ships import ship
from space_bots.torp import Torp


class Tank(ship.Ship):
    """Tank: A Tank ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='tank')

        # Tank specific stuff
        self.protect_target = None
        self.p.damage_modifier = 0.75  # 25% reduction
        self.collision_radius *= 1.1  # Tanks need their space
        self.shield_thrown = False
        self.squad_buffs = ['protection']
        self.torp_range = 200
        self.torps = []
        self.next_torp_reload = 0

        # Tank Level adjustments
        self.level = level
        self.p.hp *= self.level
        self.s.hp = self.p.hp
        self.p.shield *= self.level
        self.s.shield = self.p.shield
        self.p.shield_recharge *= self.level
        self.p.hull_recharge *= self.level

    def expire_torps(self, now):
        for t in self.torps:
            if now > t.expire:
                t.delete_me = True

    def update(self):
        """Update the Tank"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()

        # Tank specific stuff
        self.shield_thrown = False if not self.squad_in_combat() else self.shield_thrown

        # Delete dead/exploded torps
        now = time.time()
        self.expire_torps(now)
        self.torps = [t for t in self.torps if not t.delete_me]

        # Fire new Torps
        if self.s.target and force_utils.distance_between(self, self.s.target) < self.torp_range:
            if now > self.next_torp_reload:
                if len(self.torps) < 8:
                    t = Torp(self, self.game_engine, self.x, self.y)
                    self.torps.append(t)
                self.next_torp_reload = now + 0.1
            for torp in self.torps:
                torp.update()

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

        # Now actually call the move command
        self.move()


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
