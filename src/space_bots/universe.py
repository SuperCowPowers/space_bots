"""Universe: Class that contains all the stuff"""
from random import randint

# Local Imports
from space_bots import display_adapter
from space_bots import planet, ship


class Universe():
    """Universe: Class that contains all the stuff"""
    # Note: Maybe refactor/rethink how this class should be used later

    def __init__(self, width=1600, height=1000, planets=8, ships=1):
        """Initialize the Universe class"""
        self.pad = 100
        self.width = width
        self.height = height
        self.display = display_adapter.DisplayAdapter(width, height)
        self.display.set_background_color((30, 30, 40))

        # Add Planets
        self.planets = []
        for _ in range(planets):
            self.add_planet()

        # Space Planets Apart from each other

        # Add Ships
        self.ships = []
        for _ in range(ships):
            self.add_ship()

    def add_planet(self):
        """Add a Planet to the Universe"""
        new_planet = planet.Planet(self.display,
                                   x=randint(self.pad, self.width-self.pad),
                                   y=randint(self.pad, self.height-self.pad),
                                   color=self._random_color(),
                                   radius=25)
        self.planets.append(new_planet)

        # Register with the display adapter
        self.display.register_actor(new_planet)

    def add_ship(self):
        """Add a Ship to the Universe"""
        new_ship = ship.Ship(self.display,
                             x=randint(self.pad, self.width - self.pad),
                             y=randint(self.pad, self.height - self.pad))
        self.ships.append(new_ship)

        # Register with the display adapter
        self.display.register_actor(new_ship)

    def go(self):
        """Have the Universe enter it's main event loop"""
        self.display.event_loop()

    @staticmethod
    def _random_color():
        """Helper to create a random RGB color"""
        red = randint(50, 200)
        green = randint(50, 200)
        blue = randint(50, 200)
        return red, green, blue


# Simple test of the Universe functionality
def test():

    """Test for Universe Class"""

    # Create our Universe
    my_universe = Universe(1600, 1000)
    my_universe.go()


if __name__ == "__main__":
    test()
