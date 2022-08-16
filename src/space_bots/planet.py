"""Planet: Class for the Planets in Space Bots"""

# Local Imports
from space_bots import actor


class Planet(actor.Actor):
    """Planet: Class for the Planets in Space Bots"""

    def __init__(self, display_adapter, x, y, color, radius):

        # Call my superclass init
        super().__init__(display_adapter, x, y)

        # Set my attributes
        self.color = color
        self.radius = radius

    def update(self):
        """Update the Planet"""
        pass

    def draw(self):
        """Draw the entire Planet"""
        self.draw_planet()
        self.draw_shield()

    def draw_planet(self):
        """Draw the Planet Icon"""
        self.display.draw_circle(self.color, (self.x, self.y), self.radius, width=0)

    def draw_shield(self):
        """Draw the Shield"""
        self.display.draw_circle((255, 255, 255), (self.x, self.y), self.radius + 10)


# Simple test of the Planet functionality
def test():
    """Test for Planet Class"""
    from space_bots import display_adapter

    # Create our display_adapter
    my_display = display_adapter.DisplayAdapter()

    # Create our Planet
    my_planet = Planet(my_display, 100, 100, (100, 220, 200), 25)

    # Register the Actor with the Display Adapter
    my_display.register_actor(my_planet)
    my_display.event_loop()


if __name__ == "__main__":
    test()
