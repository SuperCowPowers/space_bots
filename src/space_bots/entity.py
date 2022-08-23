"""Entity: Abstract Base Class for all object (ships, planets, etc)"""
from abc import ABC, abstractmethod

# Local Imports
from space_bots import force_utils


class Entity(ABC):
    """Entity: Abstract Base Class for all object (ships, planets, etc)"""
    def __init__(self, game_engine, x=500, y=500, speed=0.1, mass=10, collision_radius=10):
        self.game_engine = game_engine
        self.x = x
        self.y = y
        self.speed = speed
        self.mass = mass
        self.collision_radius = collision_radius
        self.force_x = 0
        self.force_y = 0
        self.force_damp = 0.99

    @abstractmethod
    def communicate(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def move(self):
        """Move the Entity based on the current set of forces and mass"""
        force_utils.force_based_movement(self, self.speed)

        # Damping the force for next time
        self.force_x *= self.force_damp
        self.force_y *= self.force_damp


# Simple test of the Entity functionality
def test():
    """Test for Entity Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create an example Entity Class (needs communicate(), update() and draw() methods)
    class SimpleEntity(Entity):
        def communicate(self):
            pass

        def update(self):
            self.move()

        def draw(self):
            print('SimpleEntity: draw called..')
            self.game_engine.draw_circle((255, 255, 255), (self.x, self.y), 25)
    simple_entity = SimpleEntity(my_game_engine)
    my_universe.add_entity(simple_entity)

    # Give the entity a push
    simple_entity.force_x = 10
    simple_entity.force_y = 5

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
