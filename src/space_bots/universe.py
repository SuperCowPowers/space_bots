"""Universe: Class that contains all the stuff"""
from random import randint

# Local Imports
from space_bots import display_adapter
from space_bots import planet, squad


class Universe():
    """Universe: Class that contains all the stuff"""
    # Note: Maybe refactor/rethink how this class should be used later

    def __init__(self, width=1600, height=1000, planets=8, ships=5):
        """Initialize the Universe class"""
        self.pad = 150
        self.ship_pad = 50
        self.width = width
        self.height = height
        self.display = display_adapter.DisplayAdapter(width, height)
        self.display.set_background_color((30, 30, 30))
        self.display.set_collision_detector(self.collision_detection)

        # Add Squads/Ships
        self.squads = [
            squad.Squad(self, 12, 'red', target_strategy='low_health', stance='offensive', initial_pos=(200, 200)),
            squad.Squad(self, 8, 'green', target_strategy='nearest', stance='offensive',  initial_pos=(200, 800)),
            squad.Squad(self, 8, 'purple', target_strategy='random', stance='offensive', initial_pos=(1400, 200)),
            squad.Squad(self, 8, 'blue', target_strategy='nearest', stance='defensive', initial_pos=(1400, 800))
        ]

        # Add the Squads as Event subscribers
        for _squad in self.squads:
            self.display.add_event_subscriber(_squad)

        # We need a list of individual ships for collision detections
        self.ships = [ship for _squad in self.squads for ship in _squad.ships]

        # Add Planets
        self.planets = []
        for _ in range(planets):
            self.add_planet()

        # Space Planets Apart from each other
        self._space_out_planets()

        # Add the Planets as Event subscribers
        for _planet in self.planets:
            self.display.add_event_subscriber(_planet)

    def add_planet(self):
        """Add a Planet to the Universe"""
        new_planet = planet.Planet(self,
                                   x=randint(self.pad, self.width-self.pad),
                                   y=randint(self.pad, self.height-self.pad),
                                   color=self._random_planet_color(),
                                   radius=35)
        self.planets.append(new_planet)

        # Register with the display adapter
        self.display.register_actor(new_planet)

    def remove_ship(self, ship):
        """Remove a Ship from the Universe"""
        self.ships.remove(ship)

        # Register with the display adapter
        self.display.remove_actor(ship)

    def adversary_ships(self, squad):
        """A Squad can ask for adversary ships (not on my team)"""
        return [s for s in self.ships if s.team != squad.team]

    def go(self):
        """Have the Universe enter it's main event loop"""
        self.display.event_loop()

    def collision_detection(self, actor_list):
        """Detect if any actor is colliding with another actor"""

        # First ships against planets
        for _ship in self.ships:
            for _planet in self.planets:
                if _ship.collides(_planet):
                    _ship.move_towards(_planet, -5)

        # Second ships against ships
        for _ship in self.ships:
            for co_ship in self.ships:
                if _ship == co_ship:
                    continue
                if _ship.collides(co_ship):
                    _ship.move_towards(co_ship, -5)

        # Last ships against boundaries
        for _ship in self.ships:
            _ship.x = min(max(_ship.x, self.ship_pad), self.width-self.ship_pad)
            _ship.y = min(max(_ship.y, self.ship_pad), self.height-self.ship_pad)

    def _space_out_planets(self):
        """Make sure planets don't overlap"""
        for _ in range(50):
            for _planet in self.planets:
                for co_planet in self.planets:
                    # Skip self
                    if _planet == co_planet:
                        continue
                    # Move if too close
                    if _planet.distance_to(co_planet) < 400:
                        _planet.move_towards(co_planet, -30)
                    # Boundaries
                    _planet.x = max(min(_planet.x, self.width-self.pad), self.pad)
                    _planet.y = max(min(_planet.y, self.height-self.pad), self.pad)

    @staticmethod
    def _random_planet_color():
        """Helper to create a random RGB color"""
        # Browish
        red = randint(140, 160)
        green = randint(120, 140)
        blue = randint(70, 90)
        return red, green, blue


# Simple test of the Universe functionality
def test():

    """Test for Universe Class"""

    # Create our Universe
    my_universe = Universe(1600, 1000)
    my_universe.go()


if __name__ == "__main__":
    test()
