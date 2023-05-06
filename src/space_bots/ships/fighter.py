"""Fighter: A Fighter ship in Space Bots"""

# Local Imports
from space_bots.ships import ship
from space_bots.utils import weapon, laser_guns


class Fighter(ship.Ship):
    """Fighter: A Fighter ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='fighter', level=level)

        # Fighter specific stuff
        self.self_buffs = []  # ['first_strike'] Needs a rework
        self.mad_thrown = False  # Need to expire buffs

        # Fighter Level adjustments
        pass

        # Weapons
        self.laser_guns = laser_guns.LaserGuns(self, mount_points=2)  # Twin Laser :)
        self.torp_launcher = weapon.NoWeapon(self)

    def update(self):
        """Update the Ship"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        self.general_avoidance()
        self.general_target_movement(aggressive=1.5)

        # If the Fighter gets low health cast buff
        if self.health_percent() < .25 and not self.mad_thrown:
            print('Fighter: Now Im Mad!')
            self.announcer_messages.put('fighter_now_im_mad')
            self.add_buff('now_im_mad')
            self.mad_thrown = True

        # Now actually call the move command
        self.move()


# Simple test of the Fighter functionality
def test():
    """Test for Fighter Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.ship import Ship
    from space_bots.ships.healer import Healer

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 700, 400)
    my_universe.add_asteroid(my_asteroid)

    # Create a Fighter, Healer, and Zerg Ship
    fighter = Fighter(my_game_engine, 300, 400)
    my_universe.add_ship(fighter, team='earth')
    healer_ship = Healer(my_game_engine, 300, 400, level=2)
    my_universe.add_ship(healer_ship, team='earth')

    zerg = Ship(my_game_engine, 500, 700, ship_type='berserker')
    my_universe.add_ship(zerg, team='zerg')
    # Hack the zerg ship (no targeting)
    # zerg.general_targeting = lambda: None
    zerg = Ship(my_game_engine, 500, 700, ship_type='berserker')
    my_universe.add_ship(zerg, team='zerg')
    # Hack the zerg ship (no targeting)
    # zerg.general_targeting = lambda: None

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
