"""Planet: Class for the Planets in Space Bots"""
import os

# Local Imports
from space_bots import entity


class Planet(entity.Entity):
    """Planet: Class for the Planets in Space Bots"""

    def __init__(self, game_engine, x, y):

        # Set my attributes
        self.radius = 35  # Hard coded for now
        self.collision_radius = self.radius + 10

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=1000, collision_radius=self.collision_radius)

        # Grab our planet image
        image_path = os.path.join(os.path.dirname(__file__), 'images/planet_brown.png')
        self.planet_image = game_engine.image_load(image_path, 80, 80)
        self.image_x = self.x - self.radius - 5
        self.image_y = self.y - self.radius - 5

    def communicate(self):
        """The Planet can communicate to what?"""
        pass

    def update(self):
        """Update the Planet"""
        # Even though this seems weird... planets CAN move so make sure image goes along with
        self.image_x = self.x - self.radius - 5
        self.image_y = self.y - self.radius - 5

    def draw(self):
        """Draw the entire Planet"""
        self.draw_planet()
        self.draw_shield()

    def draw_planet(self):
        """Draw the Planet Icon"""
        self.game_engine.draw_image(self.planet_image, self.image_x, self.image_y)

    def draw_shield(self):
        """Draw the Shield"""
        self.game_engine.draw_circle((128, 128, 220), (self.x, self.y), self.radius+2, width=5)


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
