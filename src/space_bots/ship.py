"""Ship: Class for the ships in Space Bots"""

# Local Imports
from space_bots import actor


class Ship(actor.Actor):
    """Ship: Class for the ships in Space Bots"""

    def update(self):
        """Update the Ship"""
        pass

    def draw(self):
        """Draw the entire ship"""
        self.draw_ship()
        self.draw_shield()

    def draw_ship(self):
        """Draw the Ship Icon"""
        center = (self.x, self.y)
        radius = 25
        points = ((center[0], center[1] - radius * .8), (center[0] - radius * .6, center[1] + radius * .4),
                  (center[0] + radius * .6, center[1] + radius * .4))
        self.display.draw_polygon((50, 220, 50), points)

    def draw_shield(self):
        """Draw the Shield"""
        center = (self.x, self.y)
        radius = 25
        self.display.draw_circle((255, 255, 255), center, radius)


# Simple test of the Ship functionality
def test():
    """Test for Ship Class"""
    from space_bots import display_adapter

    # Create our display_adapter
    my_display = display_adapter.DisplayAdapter()

    # Create our ship
    my_ship = Ship(my_display)

    # Register the Actor with the Display Adapter
    my_display.register_actor(my_ship)
    my_display.event_loop()


if __name__ == "__main__":
    test()
