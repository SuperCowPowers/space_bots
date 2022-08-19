"""Actor: Abstract Base Class for all object (ships, planets, etc)"""
from abc import ABC, abstractmethod
import math

# Credits: Even though we're not using PyGame Zero we are inspired/using code from
#          https://www.aposteriori.com.sg/pygame-zero-helper/
#          Please visit their site and support them :)


class Actor(ABC):
    """Actor: Abstract Base Class for all object (ships, planets, etc)"""

    def __init__(self, universe, x=100, y=100):
        self.universe = universe
        self.display = universe.display
        self.x = x
        self.y = y
        self.force_x = 0
        self.force_y = 0
        self.angle = 0
        self.collision_radius = None  # This collision radius needs to be set
        self.collisions = set()  # Set of actors colliding with this actor

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    def reset_collisions(self):
        self.collisions = set()

    def collides(self, actor):
        if self.distance_to(actor) < (self.collision_radius + actor.collision_radius):
            self.collisions.add(actor)
            return True
        return False

    def in_collision(self):
        return self.collisions

    def distance_to(self, actor):
        dx = actor.x - self.x
        dy = actor.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def direction_to(self, actor):
        dx = actor.x - self.x
        dy = self.y - actor.y
        angle = math.degrees(math.atan2(dy, dx))
        if angle > 0:
            return angle
        return 360 + angle

    def move_towards(self, actor, dist):
        angle = math.radians(self.direction_to(actor))
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def point_towards(self, actor):
        self.angle = self.direction_to(actor)

    def move_in_direction(self, dist):
        angle = math.radians(self.direction)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy


# Simple test of the Actor functionality
def test():
    """Test for Actor Class"""
    from space_bots import display_adapter

    # Create a fake universe (just for testing)
    class Universe:
        pass
    Universe.display = display_adapter.DisplayAdapter()

    # Create an example Actor Class (needs update() and draw() methods)
    class SimpleActor(Actor):
        def update(self):
            pass

        def draw(self):
            self.display.draw_circle((255, 255, 255), (250, 250), 25)
    simple_actor = SimpleActor(Universe)

    # Register the Actor with the Display Adapter
    Universe.display.register_actor(simple_actor)
    Universe.display.event_loop()


if __name__ == "__main__":
    test()
