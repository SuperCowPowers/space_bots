"""Asteroid: Class for the Asteroids in Space Bots"""
import os
import math
from random import random, randint

# Local Imports
from space_bots import entity


class Asteroid(entity.Entity):
    """Asteroid: Class for the Asteroids in Space Bots"""

    def __init__(self, game_engine, x, y, mineral='blue', concentration=50):

        # Set attributes needed for super class
        self.radius = 35  # Hard coded for now
        self.collision_radius = self.radius + 10

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=1000, collision_radius=self.collision_radius)

        # Grab our asteroid image
        image_path = os.path.join(os.path.dirname(__file__), 'images/planet_brown.png')
        self.asteroid_image = game_engine.image_load(image_path, 80, 80)
        self.img_width, self.img_height = self.asteroid_image.get_size()
        self.image_offset_x = self.img_width/2
        self.image_offset_y = self.img_height/2
        self.image_x = self.x - self.image_offset_x
        self.image_y = self.y - self.image_offset_y

        # Set additional asteroid attributes
        self.force_x = randint(-100, 100)
        self.force_y = randint(-100, 100)
        self.force_damp = 1.0
        self.mineral = mineral
        self.concentration = randint(0, concentration)

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
        mineral_radius = self.radius/1.3
        for _ in range(self.concentration):
            alpha = 2 * math.pi * random()  # Random Angle
            radius = mineral_radius * random()  # Random Radius
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
        self.draw_glow()

    def draw_asteroid(self):
        """Draw the Asteroid Icon"""
        self.game_engine.draw_image(self.asteroid_image, self.image_x, self.image_y)

    def draw_minerals(self):
        """Draw the minerals for this asteroid"""
        for pos in self.mineral_locations[:int(self.concentration)]:
            self.game_engine.draw_mineral((120, 120, 255), (self.x+pos[0], self.y+pos[1]), radius=4)

    def draw_glow(self):
        """Draw the Asteroid Glow"""
        self.game_engine.draw_circle((120, 120, 255), (self.x-1, self.y), self.radius, width=3)


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
