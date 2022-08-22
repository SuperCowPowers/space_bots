"""Entity: Abstract Base Class for all object (ships, planets, etc)"""
from abc import ABC, abstractmethod
import math


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

    def collides(self, target):
        if self.distance_to(target) < (self.collision_radius + target.collision_radius):
            return True
        return False

    def distance_to(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def force_delta(self, target):
        # Force delta is based on mass of the source and target
        dx, dy = self.pos_delta(target)
        mass_ratio = target.mass/self.mass
        dx *= mass_ratio
        dy *= mass_ratio
        return dx, dy

    def pos_delta(self, target, factor=1.0):
        return (target.x - self.x)*factor, (target.y - self.y)*factor

    def move(self):
        """Move the Entity based on the current set of forces and mass"""
        delta_x = self.force_x / self.mass
        delta_y = self.force_y / self.mass
        delta_x = max(min(delta_x, self.speed), -self.speed)
        delta_y = max(min(delta_y, self.speed), -self.speed)
        self.x += delta_x
        self.y += delta_y

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
