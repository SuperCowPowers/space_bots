"""Tank: A Tank ship in Space Bots"""

# Local Imports
from space_bots.utils import weapon, torp_launcher
from space_bots.ships import ship


class Tank(ship.Ship):
    """Tank: A Tank ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='tank', level=level)

        # Tank specific stuff
        self.protect_target = None
        self.p.incoming_damage_modifier *= 0.7  # 30% reduction
        self.pad_radius += 10  # Tanks need their space
        self.shield_thrown = False
        self.iron_will_thrown = False
        self.squad_buffs = ['protection']

        # Tank Level adjustments (Super Size Me)
        self.p.hp *= (0.8 + self.level/5.0)
        self.p.shield *= (0.8 + self.level/5.0)
        # self.p.radius = int(self.p.radius * (0.9 + self.level/10.0))
        self.s.hp = self.p.hp
        self.s.shield = self.p.shield

        # Weapons
        self.laser_guns = weapon.NoWeapon(self)  # Tanks don't have lasers
        self.torp_launcher = torp_launcher.TorpLauncher(self, self.p.max_torps, level)

    def update(self):
        """Update the Tank"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        self.general_target_movement(aggressive=2.0)

        # Track the lowest health TeamMate
        self.protect_target = self.battle_info.lowest_health_teammate(self)
        if not self.shield_thrown and self.protect_target.health_percent() < .15:
            print('Tank: Take the Pain!')
            self.announcer_messages.put('tank_cast_pain')
            self.protect_target.add_buff('take_the_pain')
            self.shield_thrown = True

        # Cast Iron Will
        if False and self.protect_target.health_percent() < .07 and not self.iron_will_thrown:
            self.announcer_messages.put('tank_cast_iron_will')
            for _ship in self.squad.ships:
                _ship.add_buff('iron_will')
            self.iron_will_thrown = True

        # Now actually call the move command
        self.move()


# Simple test of the Tank functionality
def test():
    """Test for Tank Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.healer import Healer
    from space_bots.ships.ship import Ship

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 800, 500)
    my_universe.add_asteroid(my_asteroid)

    # Create a Healer ship and a Tank Ship
    healer_ship = Healer(my_game_engine, 400, 400)
    my_universe.add_ship(healer_ship, team='earth')
    tank = Tank(my_game_engine, 300, 300)
    my_universe.add_ship(tank, team='earth')

    # Add a Zerg enemy
    zerg = Ship(my_game_engine, 500, 700, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')
    # zerg.general_targeting = lambda: None     # Hack the zerg ship (no targeting)

    # Give the tank some damage to heal up
    tank.damage(500)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
