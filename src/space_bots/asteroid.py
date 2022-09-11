"""Asteroid: Class for the Asteroids in Space Bots"""
import os
import math
from random import randint, choice

# Local Imports
from space_bots import entity


# FIXME
minerals = {'blue': (140, 140, 255),
            'green': (120, 220, 120),
            'yellow': (210, 240, 100),
            'orange': (255, 200, 80)
            }


class Asteroid(entity.Entity):
    """Asteroid: Class for the Asteroids in Space Bots"""

    def __init__(self, game_engine, x, y, mineral='blue', concentration=30):

        # Set attributes needed for super class
        self.radius = 35  # Hard coded for now
        self.collision_radius = self.radius + 10

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=1000, collision_radius=self.collision_radius)

        # Grab our asteroid image
        image_path = os.path.join(os.path.dirname(__file__), 'images/planet_brown.png')
        self.asteroid_image = game_engine.image_load(image_path)
        self.img_width, self.img_height = self.asteroid_image.get_size()
        self.image_offset_x = self.img_width/2
        self.image_offset_y = self.img_height/2
        self.image_x = self.x - self.image_offset_x
        self.image_y = self.y - self.image_offset_y

        # Set additional asteroid attributes
        self.force_x = randint(-200, 200)
        self.force_y = randint(-200, 200)
        self.force_damp = 1.0
        self.mineral = minerals[choice(list(minerals.keys()))]
        self.concentration = randint(10, concentration)

        # Precompute mineral locations
        self.mineral_locations = self.precompute_minerals()

    def extract_minerals(self, amount):
        """Extract Minerals from this Asteroid"""
        if self.concentration > amount:
            self.concentration -= amount
            return amount
        else:
            extracted_amount = self.concentration
            self.concentration = 0
            return extracted_amount

    def precompute_minerals(self):
        """Precompute Mineral positions"""
        positions = []
        mineral_radius = self.radius/1.4
        alpha = 0
        radius = 1
        alpha_delta = 2.0 * math.pi / 6
        radius_delta = mineral_radius / 25
        for _ in range(self.concentration):
            alpha += alpha_delta
            alpha_delta *= .95
            radius += radius_delta
            radius_delta *= .95
            x = radius * math.cos(alpha)
            y = radius * math.sin(alpha)
            positions.append((x, y))
        return positions

    def damage(self, points):
        """Inflict damage on this Asteroid"""
        pass

    def communicate(self, comms):
        """The Asteroid can communicate to what?"""
        pass

    def update(self):
        """Update the Asteroid"""
        # Even though this seems weird... asteroids CAN move so make sure image goes along with
        self.image_x = self.x - self.image_offset_x
        self.image_y = self.y - self.image_offset_y
        self.move()

    def draw(self):
        """Draw the entire Asteroid"""
        self.draw_asteroid()
        self.draw_minerals()
        self.draw_outline()

    def draw_asteroid(self):
        """Draw the Asteroid Icon"""
        self.game_engine.draw_image(self.asteroid_image, self.image_x, self.image_y)

    def draw_minerals(self):
        """Draw the minerals for this asteroid"""
        for pos in self.mineral_locations[:int(self.concentration)]:
            self.game_engine.draw_mineral(self.mineral, (self.x+pos[0], self.y+pos[1]), radius=5)

    def draw_outline(self):
        """Draw the Asteroid Outline"""
        self.game_engine.draw_circle((0, 0, 0), (self.x, self.y), self.radius-1, width=2)


# Simple test of the Asteroid functionality
def test():
    """Test for Asteroid Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = Asteroid(my_game_engine, 200, 200)
    my_universe.add_asteroid(my_asteroid)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
