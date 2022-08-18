"""Ship: Class for the ships in Space Bots"""
import random
import math

# Local Imports
from space_bots import actor


class Ship(actor.Actor):
    """Ship: Class for the ships in Space Bots"""
    team_colors = {'blue': (100, 100, 255),
                   'green': (80, 200, 80),
                   'red': (200, 80, 80),
                   'purple': (180, 50, 220)}

    def __init__(self, universe, x, y, team, radius=12, strategy='random', stance='defensive'):

        # Call my superclass init
        super().__init__(universe, x, y)

        # Set my attributes
        self.universe = universe
        self.team = team
        self.speed = 0.5
        self.color = self.team_colors[team]
        self.radius = radius
        self.shield_radius = radius + 5
        self.collision_radius = radius + 7
        self.laser_range = 120
        self.hp = 200
        self.shield = 250
        self.shield_recharge = 0.005
        self.total_health = 350
        self.target = None
        self.adversaries = None
        self.non_targets = []
        self.strategy = strategy
        self.stance = stance
        self.run_away_factor = 0.3
        if self.stance == 'defensive':
            self.stay_away_distance = 200  # Just outside of laser range
        else:
            self.stay_away_distance = 0

    def post_init(self):
        # Get a list of other ships
        self.adversaries = self.universe.adversary_ships(self)

    def damage(self, points):
        """Inflict damage on this ship"""
        if self.shield:
            self.shield = max(self.shield - points, 0)
        else:
            self.hp = max(self.hp-points, 0)

    def health(self):
        return self.shield + self.hp

    def low_health(self):
        return self.health() < self.total_health * 0.5

    def is_dead(self):
        return self.hp == 0

    def lowest_health(self, ships):
        ship_health = [(s, s.health()) for s in ships]
        ship_health.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_health]

    def closest(self, ships):
        ship_distance = [(s, s.distance_to(self)) for s in ships]
        ship_distance.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_distance]

    def next_target(self):
        """Select my next target based on a Strategy"""
        # Attack the adversary with the lowest health
        if self.strategy == 'low_health':
            return self.lowest_health(self.adversaries)[0]
        if self.strategy == 'closest':
            return self.closest(self.adversaries)[0]
        if self.target is None:
            return random.choice(self.adversaries)
        else:
            return self.target

    def update(self):
        """Update the Ship"""

        # Am I dead?
        if self.is_dead():
            return

        # Is everyone else dead?
        if not self.adversaries:
            return

        # Shield recharge
        self.shield += self.shield_recharge
        self.shield = min(self.shield, 250)
        self.target = self.next_target()
        self.non_targets = self.adversaries.copy()
        self.non_targets.remove(self.target)

        # Move Towards (Attack)
        if self.distance_to(self.target) > self.laser_range/4:
            self.move_towards(self.target, self.speed)

        # Low Health Defensive
        if self.stance == 'defensive':
            if self.low_health():
                self.run_away_factor = 1.0
            else:
                self.run_away_factor = 0.25

        # Move Away from Others
        for ship in self.non_targets:
            if self.distance_to(ship) < self.stay_away_distance:
                self.move_towards(ship, -self.speed*self.run_away_factor)

        # Is my target dead?
        if self.target.is_dead():
            self.adversaries = [s for s in self.adversaries if not s.is_dead()]
            if self.adversaries:
                self.target = random.choice(self.adversaries)
                self.non_targets = self.adversaries.copy()
                self.non_targets.remove(self.target)
            else:
                self.target = None
                self.adversaries = []
                self.non_targets = []

    def draw(self):
        """Draw the entire ship"""
        if self.hp == 0:
            self.universe.remove_ship(self)
        else:
            self.draw_laser()
            self.draw_ship()
            if self.shield:
                self.draw_shield()

    def draw_ship(self):
        """Draw the Ship Icon"""
        self.display.draw_circle(self.color, (self.x, self.y), self.radius, width=4)
        if self.low_health():
            self.display.draw_circle((240, 240, 240), (self.x, self.y), 4)
        # self.display.draw_circle((100, 100, 100), (self.x, self.y), self.radius-3)

    def draw_dead(self):
        """Draw the Dead Ship Icon"""
        self.display.draw_circle((0, 0, 0), (self.x, self.y), self.radius)

    def draw_laser(self):
        """Draw the laser"""
        if self.target and self.distance_to(self.target) < self.laser_range:
            self.display.draw_line(self.color, (self.x, self.y), (self.target.x, self.target.y), width=4)
            self.target.damage(0.2)

    def draw_direction(self, actor):
        """Draw an indicator for the Ship's direction"""
        # FIXME: Has to be a better/nicer way
        angle = math.radians(self.angle)
        dist = self.radius * 2
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.display.draw_line(self.color, (self.x-1, self.y-1), (self.x + dx, self.y - dy))

    def draw_shield(self):
        """Draw the Shield"""
        shield_color = (self.shield, self.shield, self.shield)
        self.display.draw_circle(shield_color, (self.x, self.y), self.shield_radius, width=2)


# Simple test of the Ship functionality
def test():
    """Test for Ship Class"""
    from space_bots.universe import Universe

    # Create a fake universe (just for testing)
    my_universe = Universe(1600, 1000)

    # Create our ship
    my_ship = Ship(my_universe, 100, 100, 'blue', 20)

    # Register the Actor with the Display Adapter
    Universe.display.register_actor(my_ship)
    Universe.display.event_loop()


if __name__ == "__main__":
    test()
