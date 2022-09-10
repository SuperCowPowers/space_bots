"""Planet: Class for the Planets in Space Bots"""
import os
import random

# Local Imports
from space_bots import entity


class Planet(entity.Entity):
    """Planet: Class for the Planets in Space Bots"""

    def __init__(self, game_engine, x, y):

        # Set attributes needed for super class
        self.radius = 35  # Hard coded for now
        self.collision_radius = self.radius + 10

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=1000, collision_radius=self.collision_radius)

        # Grab our planet image
        image_path = os.path.join(os.path.dirname(__file__), 'images/planet_brown.png')
        self.planet_image = game_engine.image_load(image_path, 80, 80)
        self.img_width, self.img_height = self.planet_image.get_size()
        self.image_offset_x = self.img_width/2
        self.image_offset_y = self.img_height/2
        self.image_x = self.x - self.image_offset_x
        self.image_y = self.y - self.image_offset_y

        # Set additional planet attributes
        self.rotation = 0
        self.rotation_delta = random.uniform(-0.5, 0.5)
        self.force_x = random.randint(-100, 100)
        self.force_y = random.randint(-100, 100)
        self.force_damp = 1.0

    def communicate(self, comms):
        """The Planet can communicate to what?"""
        pass

    def update(self):
        """Update the Planet"""
        # Even though this seems weird... planets CAN move so make sure image goes along with
        self.image_x = self.x - self.image_offset_x
        self.image_y = self.y - self.image_offset_y
        self.rotation += self.rotation_delta
        self.move()

    def draw(self):
        """Draw the entire Planet"""
        self.draw_planet()
        self.draw_glow()

    def draw_planet(self):
        """Draw the Planet Icon"""
        self.game_engine.draw_image(self.planet_image, self.image_x, self.image_y, self.rotation)

    def draw_glow(self):
        """Draw the Planet Glow"""
        self.game_engine.draw_circle((120, 120, 255), (self.x-1, self.y), self.radius, width=5)


# Simple test of the Planet functionality
def test():
    """Test for Planet Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Planet
    my_planet = Planet(my_game_engine, 200, 200)
    my_universe.add_planet(my_planet)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
