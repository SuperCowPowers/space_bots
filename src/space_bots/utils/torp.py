"""Torp: Class for the Torpedoes in Space Bots"""

# Local Imports
from space_bots import entity
from space_bots.utils import force_utils


class Torp(entity.Entity):
    """Torp: Class for the Torpedoes in Space Bots"""
    def __init__(self, origin_ship, level=1):

        # Set my Torp Parameters
        self.origin_ship = origin_ship
        self.target = None
        self.level = level
        self.damage = level * 10
        self.mass = 10
        self.speed = None
        self.color = origin_ship.p.color
        self.released = False
        self.release_counter = 0
        self.expire = 300

        # Call SuperClass (Entity) Initialization
        super().__init__(origin_ship.game_engine, origin_ship.x, origin_ship.y, mass=self.mass, speed=self.speed)

        # Torps don't slow down
        self.force_damp = 1.0

    def set_target(self, target):
        """Set the Torp Target"""
        self.target = target

    def pre_delete(self):
        """All Entities have a pre_delete method where they might take some action/set stuff before being deleted"""
        pass

    def impact(self, ship):
        """The Torp has impacted an enemy ship"""
        ship.damage(self.damage)
        self.delete_me = True

    def communicate(self, comms):
        """Communicate"""
        pass  # Torps don't say much

    def update(self):
        """Update the Torp"""

        # Check for Torp Expiration
        if self.released:
            self.release_counter += 1
            if self.release_counter > self.expire:
                self.delete_me = True
                return

        # Guidance Initiated?
        if self.release_counter > 50 and self.target:
            (dx, dy), (_, _) = force_utils.attack_forces(self, self.target)
            self.force_x += dx
            self.force_y += dy

        # Now actually call the move command
        self.move()

    def draw(self):
        """Draw the torpedo"""
        self.game_engine.draw_circle(self.color, (self.x, self.y), 3, width=0)
        self.game_engine.draw_circle((220, 220, 220), (self.x, self.y), 4, width=1)


# Simple test of the Torp functionality
def test():
    """Test for Torp Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe
    from space_bots.ships.tank import Tank
    from space_bots.ships.ship import Ship

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Tank and fire some torps
    tank = Tank(my_game_engine, 400, 400)
    my_universe.add_ship(tank, team='earth')
    tank.speed = 0.1

    zerg = Ship(my_game_engine, 400, 800, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')
    zerg.speed = 0.1

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
