"""Ship: Class for the ships in Space Bots"""
import math

# Local Imports
from space_bots import actor


class Ship(actor.Actor):
    """Ship: Class for the ships in Space Bots"""
    def __init__(self, universe, x, y, squad, radius=12, strategy='random', stance='defensive'):

        # Call my superclass init
        super().__init__(universe, x, y)

        # Set my attributes
        self.universe = universe
        self.squad = squad
        self.team = squad.team
        self.color = self.squad.team_colors[self.team]
        if strategy == 'low_health':
            self.speed = 1.5
        else:
            self.speed = 0.25
        self.radius = radius
        self.shield_radius = radius + 5
        self.collision_radius = radius + 7
        self.laser_range = 150
        self.laser_damage = 0.2
        self.hp = 200
        self.shield = 250
        self.shield_recharge = 0.01
        self.total_health = 350
        self.target = None
        self.non_targets = []
        self.strategy = strategy
        self.stance = stance
        self.run_away_factor = 0.2
        self.force_x = 0
        self.force_y = 0
        if self.stance == 'defensive':
            self.stay_away_distance = self.laser_range + 20
        else:
            self.stay_away_distance = 0

    def within_range(self, target):
        """Is this target within weapons range"""
        return self.distance_to(target) < self.laser_range

    def damage(self, points):
        """Inflict damage on this ship"""
        if self.shield:
            self.shield = max(self.shield - points, 0)
        else:
            self.hp = max(self.hp-points, 0)

    def health(self):
        return self.shield + self.hp

    def health_percent(self):
        return self.health()/self.total_health

    def low_health(self):
        return self.health_percent() < 0.5

    def is_dead(self):
        return self.hp == 0

    def position_delta(self, target, fraction=1.0):
        dx = (target[0] - self.x) * fraction
        dy = (target[1] - self.y) * fraction
        return dx, dy

    def update(self):
        """Update the Ship"""

        # Shield recharge
        self.shield += self.shield_recharge
        self.shield = min(self.shield, 250)

        # Choose the main target if it's within range, otherwise ask for secondary target
        if self.squad.main_target and self.within_range(self.squad.main_target):
            self.target = self.squad.main_target
        else:
            self.target = self.squad.secondary_target(self)

        # If I have no target, so don't update
        if self.target is None:
            return

        # Compute my non targets
        self.non_targets = self.squad.adversaries.copy()
        self.non_targets.remove(self.target)

        # Move Towards (Attack)
        if self.distance_to(self.target) > self.laser_range/4:
            delta = self.position_delta((self.target.x, self.target.y), .01)
            self.force_x += delta[0]
            self.force_y += delta[1]

        # Move Away from Others
        for ship in self.non_targets:
            if self.distance_to(ship) < self.stay_away_distance:
                delta = self.position_delta((ship.x, ship.y), .005 * 1.0/(self.health_percent()*self.health_percent()))
                self.force_x -= delta[0]
                self.force_y -= delta[1]

        # Now use the force parameters to actually move
        # self.x += self.force_x * self.speed
        # self.y += self.force_y * self.speed
        # return
        # FIXME: Improve implementation performance
        norm = math.sqrt(self.force_x*self.force_x + self.force_y*self.force_y)
        if norm:
            # Low Health Speed Boost
            boost = 2.0 if self.low_health() else 1.0
            self.x += self.force_x / norm * self.speed * boost
            self.y += self.force_y / norm * self.speed * boost

    def draw(self):
        """Draw the entire ship"""
        if self.is_dead():
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
            self.target.damage(self.laser_damage)

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
    from space_bots import display_adapter

    # Create a fake universe (just for testing)
    class Universe:
        pass
    Universe.display = display_adapter.DisplayAdapter()

    # Create our ship
    my_ship = Ship(Universe, 100, 100, 'blue', 20)

    # Register the Actor with the Display Adapter
    Universe.display.register_actor(my_ship)
    Universe.display.event_loop()


if __name__ == "__main__":
    test()
