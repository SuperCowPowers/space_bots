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

        # Add Planets
        self.planets = []
        for _ in range(planets):
            self.add_planet()

        # Space Planets Apart from each other
        self._space_out_planets()

        # Add the Planets as Event subscribers
        for _planet in self.planets:
            self.display.add_event_subscriber(_planet)

        # Add Squads/Ships
        self.squads = [
            squad.Squad(self, 10, ship_type='destroyer', team='yellow', alliance='pirates',
                        target_strategy='low_health', stance='offensive', initial_pos=(200, 200)),
            squad.Squad(self, 10, ship_type='cruiser', team='green', alliance='pirates',
                        target_strategy='nearest', stance='offensive',  initial_pos=(300, 700)),
            squad.Squad(self, 5, ship_type='battleship', team='purple', alliance='pirates',
                        target_strategy='threat', stance='offensive', initial_pos=(550, 650)),
            squad.Squad(self, 4, ship_type='cruiser', team='blue', alliance='player',
                        target_strategy='nearest', stance='defensive', initial_pos=(800, 500)),
            squad.Squad(self, 3, ship_type='battleship', team='blue', alliance='player',
                        target_strategy='threat', stance='defensive', initial_pos=(800, 500)),
            squad.Squad(self, 1, ship_type='starbase', team='blue', alliance='player',
                        target_strategy='threat', stance='defensive', initial_pos=(800, 500))
        ]
        # Protection Assignments
        self.squads[3].protect(self.squads[5])
        self.squads[4].protect(self.squads[5])
        self.squads[5].protect(self.closest_planet(self.squads[5]))
        """
        self.squads = [
            squad.Squad(self, 20, ship_type='scout', team='red', alliance='pirates',
                        target_strategy='low_health', stance='offensive', initial_pos=(500, 500)),
            squad.Squad(self, 20, ship_type='destroyer', team='yellow', alliance='pirates',
                        target_strategy='low_health', stance='offensive', initial_pos=(500, 500)),
            squad.Squad(self, 4, ship_type='battleship', team='red', alliance='pirates',
                        target_strategy='nearest', stance='offensive', initial_pos=(500, 500)),
            squad.Squad(self, 20, ship_type='scout', team='blue', alliance='player',
                        target_strategy='low_health', stance='offensive', initial_pos=(900, 800)),
            squad.Squad(self, 20, ship_type='destroyer', team='blue', alliance='player',
                        target_strategy='low_health', stance='offensive', initial_pos=(900, 800)),
            squad.Squad(self, 4, ship_type='battleship', team='blue', alliance='player',
                        target_strategy='threat', stance='offensive', initial_pos=(900, 800))
        ]

        # Protection Assignments
        # self.squads[2].protect(self.closest_planet(self.squads[4]))
        # self.squads[3].protect(self.closest_planet(self.squads[4]))
        # self.squads[4].protect(self.closest_planet(self.squads[4]))
        """

        # Add the Squads as Event subscribers
        for _squad in self.squads:
            self.display.add_event_subscriber(_squad)

        # We need a list of individual ships for collision detections
        self.ships = [ship for _squad in self.squads for ship in _squad.ships]

    def add_planet(self):
        """Add a Planet to the Universe"""
        new_planet = planet.Planet(self,
                                   x=randint(700, 900),
                                   y=randint(400, 600),
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
        """A Squad can ask for adversary ships (not in my appliance)"""
        return [s for s in self.ships if s.alliance != squad.alliance]

    def go(self):
        """Have the Universe enter it's main event loop"""
        self.display.event_loop()

    @staticmethod
    def force_delta(source, target):
        # Force delta is based on mass of the source and target
        mass_ratio = target.mass/source.mass
        dx = (target.x - source.x) * mass_ratio * mass_ratio
        dy = (target.y - source.y) * mass_ratio * mass_ratio
        return dx, dy

    def collision_detection(self, actor_list):
        """Detect if any actor is colliding with another actor"""

        # First ships against planets
        for _ship in self.ships:
            for _planet in self.planets:
                if _ship.collides(_planet):
                    delta = self.force_delta(_ship, _planet)
                    _ship.force_x -= delta[0]
                    _ship.force_y -= delta[1]

        # Second ships against ships
        for _ship in self.ships:
            for co_ship in self.ships:
                if _ship == co_ship:
                    continue
                if _ship.collides(co_ship):
                    delta = self.force_delta(_ship, co_ship)
                    _ship.force_x -= delta[0]
                    _ship.force_y -= delta[1]

        # Last ships against boundaries
        for _ship in self.ships:
            _ship.x = min(max(_ship.x, self.ship_pad), self.width-self.ship_pad)
            _ship.y = min(max(_ship.y, self.ship_pad), self.height-self.ship_pad)

    def closest_planet(self, ship):
        planet_distance = [(p, ship.distance_to(p)) for p in self.planets]
        planet_distance.sort(key=lambda tup: tup[1])
        return [p[0] for p in planet_distance][0]

    def _space_out_planets(self):
        """Make sure planets don't overlap"""
        for _ in range(50):
            for _planet in self.planets:
                for co_planet in self.planets:
                    # Skip self
                    if _planet == co_planet:
                        continue
                    # Move if too close
                    if _planet.distance_to(co_planet) < 350:
                        _planet.move_towards(co_planet, -5)
                    # Boundaries
                    _planet.x = max(min(_planet.x, self.width-self.pad), self.pad)
                    _planet.y = max(min(_planet.y, self.height-self.pad), self.pad)

    @staticmethod
    def _random_planet_color():
        """Helper to create a random RGB color"""
        # Brownish
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
