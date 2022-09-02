"""Torp: Class for the Torpedoes in Space Bots"""
import random
import time

# Local Imports
from space_bots import entity
from space_bots.utils import force_utils


class Torp(entity.Entity):
    """Torp: Class for the Torpedoes in Space Bots"""
    def __init__(self, origin_ship, game_engine, x=500, y=500, level=1):

        # Set my Torp Parameters
        self.origin_ship = origin_ship
        self.level = level
        self.damage = level * 5
        self.mass = 10
        self.speed = 1.0
        self.color = origin_ship.p.color
        self.guidance = True
        self.expire = time.time() + 3

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=self.mass, speed=self.speed)

        # Fun to slightly randomize the torp launches
        self.force_x = random.uniform(-2, 2)
        self.force_y = random.uniform(-2, 2)
        self.force_damp = 1.0

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
        # Move towards primary target until guidance wears off
        if self.origin_ship.squad.main_target:
            if self.guidance:
                (dx, dy), (_, _) = force_utils.attraction_forces(self, self.origin_ship.squad.main_target, 0)
                self.force_x += dx
                self.force_y += dy
                # If we have a reasonable force vector turn off guidance
                if abs(self.force_x) > 10 or abs(self.force_y) > 10:
                    self.guidance = False

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
    tank = Tank(my_game_engine, 300, 500)
    my_universe.add_ship(tank, team='earth')

    zerg = Ship(my_game_engine, 900, 500, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
