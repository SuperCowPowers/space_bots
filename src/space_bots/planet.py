"""Planet: Class for the Planets in Space Bots"""
import pygame

# Local Imports
from space_bots import actor


class Planet(actor.Actor):
    """Planet: Class for the Planets in Space Bots"""

    def __init__(self, universe, x, y, color, radius):

        # Call my superclass init
        super().__init__(universe, x, y)

        # Set my attributes
        self.mass = 1000
        self.color = color
        self.radius = radius
        self.collision_radius = radius

        # Grab our planet image
        self.planet_image = pygame.image.load('images/planet_brown.png')
        self.planet_image = pygame.transform.scale(self.planet_image, (80, 80))
        self.image_x = self.x
        self.image_y = self.y
        self.surface = universe.display.get_surface()

    def update(self):
        """Update the Planet"""
        self.image_x = self.x-self.radius-5
        self.image_y = self.y-self.radius-5

    def draw(self):
        """Draw the entire Planet"""
        self.draw_planet()
        self.draw_shield()

    def draw_planet(self):
        """Draw the Planet Icon"""
        self.surface.blit(self.planet_image, (self.image_x, self.image_y))

    def draw_shield(self):
        """Draw the Shield"""
        self.display.draw_circle((128, 128, 220), (self.x, self.y), self.radius+2, width=4)


# Simple test of the Planet functionality
def test():
    """Test for Planet Class"""
    from space_bots import display_adapter

    # Create a fake universe (just for testing)
    class Universe:
        pass
    Universe.display = display_adapter.DisplayAdapter()

    # Create our Planet
    my_planet = Planet(Universe, 100, 100, (100, 220, 200), 25)

    # Register the Actor with the Display Adapter
    Universe.display.register_actor(my_planet)
    Universe.display.event_loop()


if __name__ == "__main__":
    test()
