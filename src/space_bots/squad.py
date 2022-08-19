"""Squad: Class for the squads in Space Bots"""
from random import randint, choice
import statistics

# Local imports
from space_bots import ship


# FIXME
stances = {
    'defensive': {
        'clumping': 1.0,
        'avoidance': 1.0,
        'hurt': 0.35
    },
    'offensive': {
        'clumping': 0.5,
        'avoidance': 0.0,
        'hurt': 0.0
    }
}


class Squad:
    """Squad: Class for the squads in Space Bots"""
    team_colors = {'blue': (100, 100, 255),
                   'green': (80, 200, 80),
                   'red': (200, 80, 80),
                   'purple': (180, 50, 220),
                   'yellow': (180, 180, 100)
                   }

    def __init__(self, universe, num_ships, ship_type='cruiser', team='blue', target_strategy='random', stance='defensive',
                 formation='tdb', initial_pos=(200, 200)):

        # Set my attributes
        self.universe = universe
        self.num_ships = num_ships
        self.team = team
        self.color = self.team_colors[team]
        self.adversaries = None
        self.target_strategy = target_strategy
        self.main_target = None
        self.stance = stance
        self.spacing = 80
        self.initial_pos = initial_pos
        self.grid = {'min_x': universe.pad,
                     'min_y': universe.pad,
                     'max_x': universe.width-universe.pad,
                     'max_y': universe.height-universe.pad}

        # Current position (this will be the centroid of the Squad)
        self.x = initial_pos[0]
        self.y = initial_pos[1]

        # Create my Ships
        self.ships = self.create_ships(num_ships, ship_type, stance)

        # Keep a list of my adversaries (populated in update)
        self.adversaries = None

        # Capture Sticky Targets for Random and Low Health Targeting
        self.sticky_targets = {}

    def create_ships(self, num_ships, ship_type, stance):
        """Create a set of ships for this squad"""
        return [self.create_ship(ship_type, stance) for _ in range(num_ships)]

    def create_ship(self, ship_type, stance):
        """Create a Ship for this Squad"""

        # Set the initial position of the ship, this will quickly change based on formation
        init_x = self.initial_pos[0] + randint(-200, 200)
        init_y = self.initial_pos[1] + randint(-200, 200)
        new_ship = ship.Ship(self.universe, x=init_x, y=init_y,
                             squad=self, ship_type=ship_type, strategy=self.target_strategy, stance=stance)

        # Register with the Universe display adapter
        self.universe.display.register_actor(new_ship)
        return new_ship

    def update(self):
        """Update the Squad"""

        # Remove any dead ships
        self.ships = [s for s in self.ships if not s.is_dead()]

        # Get my adversaries
        self.adversaries = self.universe.adversary_ships(self)

        # Compute information about the squad
        self.x, self.y = self.compute_centroid()
        self.main_target = self.compute_main_target()

        # Clear any previous commands/movements/forces
        for _ship in self.ships:
            _ship.force_x = 0
            _ship.force_y = 0

        # Squad Movement: Group up
        if self.stance == 'defensive':
            for _ship in self.ships:
                delta = _ship.position_delta((self.x, self.y), .01)
                _ship.force_x += delta[0]
                _ship.force_y += delta[1]

        # Update each ship
        for _ship in self.ships:
            _ship.update()

    def draw(self):
        """Draw the entire squad"""
        for _ship in self.ships:
            _ship.draw()

    def compute_centroid(self):
        if not self.ships:
            return 0, 0
        x_centroid = statistics.fmean([s.x for s in self.ships])
        y_centroid = statistics.fmean([s.y for s in self.ships])
        return x_centroid, y_centroid

    def lowest_health(self):
        ship_health = [(s, s.health()) for s in self.adversaries]
        ship_health.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_health]

    def closest_to_squad(self):
        squad_distance = [(s, self.distance_centroid(s)) for s in self.adversaries]
        squad_distance.sort(key=lambda tup: tup[1])
        return [s[0] for s in squad_distance]

    def closest_to_ship(self, ship):
        ship_distance = [(s, ship.distance_to(s)) for s in self.adversaries]
        ship_distance.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_distance]

    def distance_centroid(self, target):
        dx = self.x - target.x
        dy = self.y - target.y
        return dx, dy

    def compute_main_target(self):
        """Select the squads main target based on a Strategy"""
        try:
            if self.target_strategy == 'low_health':
                return self.lowest_health()[0]
            if self.target_strategy == 'nearest':
                return self.closest_to_squad()[0]
            if self.target_strategy == 'random':
                return None  # Special Logic for Random
        except IndexError:
            return None

    def secondary_target(self, my_ship):
        """A ship might ask for a secondary target"""
        try:
            if self.target_strategy == 'low_health':
                return self.get_sticky_target(my_ship, self.lowest_health()[1:4])
            if self.target_strategy == 'nearest':
                return self.closest_to_ship(my_ship)[0]
            if self.target_strategy == 'random':
                return self.get_sticky_target(my_ship, self.adversaries)
        except IndexError:
            if self.adversaries:
                return choice(self.adversaries)
            else:
                return None

    def get_sticky_target(self, my_ship, choice_list):
        if my_ship not in self.sticky_targets:
            self.sticky_targets[my_ship] = choice(choice_list)
        elif self.sticky_targets[my_ship] not in self.adversaries:
            self.sticky_targets[my_ship] = choice(choice_list)
        return self.sticky_targets[my_ship]


# Simple test of the Squad functionality
def test():
    """Test for Squad Class"""
    from space_bots import display_adapter

    # Create a fake universe (just for testing)
    class Universe:
        def __init__(self):
            self.display = display_adapter.DisplayAdapter()
            self.pad = 150
            self.width = 1600
            self.height = 1000
    fake_universe = Universe()

    # Create a couple of squads
    Squad(fake_universe, 5, team='blue', target_strategy='nearest', stance='defensive', initial_pos=(300, 300))
    Squad(fake_universe, 5, team='green', target_strategy='random', stance='offensive', initial_pos=(800, 800))

    # Start the event loop
    fake_universe.display.event_loop()


if __name__ == "__main__":
    test()
