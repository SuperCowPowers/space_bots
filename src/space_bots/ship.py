"""Ship: Class for the ships in Space Bots"""
import math

# Local Imports
from space_bots import actor


# FIXME
ship_specs = {
    'scout':
        {'mass': 20,
         'speed': 0.75,
         'radius': 6,
         'hp': 100,
         'shield': 50,
         'laser_range': 50,
         'laser_damage': 0.05,
         'laser_width': 2,
         'ship_width': 2,
         'shield_width': 1,
         'shield_recharge': 0.0005,
         'hull_recharge': 0.0005
         },
    'destroyer':
        {'mass': 30,
         'speed': 0.5,
         'radius': 9,
         'hp': 150,
         'shield': 100,
         'laser_range': 80,
         'laser_damage': 0.1,
         'laser_width': 3,
         'ship_width': 3,
         'shield_width': 2,
         'shield_recharge': 0.001,
         'hull_recharge': 0.001
         },
    'cruiser':
        {'mass': 40,
         'speed': 0.25,
         'radius': 12,
         'hp': 200,
         'shield': 150,
         'laser_range': 120,
         'laser_damage': 0.15,
         'laser_width': 4,
         'ship_width': 3,
         'shield_width': 2,
         'shield_recharge': 0.0015,
         'hull_recharge': 0.0015
         },
    'battleship':
        {'mass': 60,
         'speed': 0.1,
         'radius': 14,
         'hp': 300,
         'shield': 200,
         'laser_range': 150,
         'laser_damage': 0.3,
         'laser_width': 5,
         'ship_width': 4,
         'shield_width': 2,
         'shield_recharge': 0.01,
         'hull_recharge': 0.01
         },
    'starbase':
        {'mass': 200,
         'speed': 0.05,
         'radius': 20,
         'hp': 800,
         'shield': 500,
         'laser_range': 250,
         'laser_damage': 1.0,
         'laser_width': 6,
         'ship_width': 5,
         'shield_width': 3,
         'shield_recharge': 0.1,
         'hull_recharge': 0.1
         }
}


class Ship(actor.Actor):
    """Ship: Class for the ships in Space Bots"""
    def __init__(self, universe, x, y, squad, ship_type='cruiser', strategy='random', stance='defensive'):

        # Call my superclass init
        super().__init__(universe, x, y)

        # Set my attributes
        self.universe = universe
        self.squad = squad
        self.team = squad.team
        self.alliance = squad.alliance
        self.color = self.squad.team_colors[self.team]

        # Parameters based on ship_type
        self.ship_type = ship_type
        self.mass = ship_specs[ship_type]['mass']
        self.speed = ship_specs[ship_type]['speed']
        self.radius = ship_specs[ship_type]['radius']
        self.hp = ship_specs[ship_type]['hp']
        self.shield = ship_specs[ship_type]['shield']
        self.laser_range = ship_specs[ship_type]['laser_range']
        self.laser_damage = ship_specs[ship_type]['laser_damage']
        self.laser_width = ship_specs[ship_type]['laser_width']
        self.shield_recharge = ship_specs[ship_type]['shield_recharge']
        self.hull_recharge = ship_specs[ship_type]['hull_recharge']
        self.ship_width = ship_specs[ship_type]['ship_width']
        self.shield_width = ship_specs[ship_type]['shield_width']
        self.shield_radius = self.radius + self.shield_width + 1
        self.collision_radius = self.radius + self.shield_width + 4
        self.total_health = self.hp + self.shield
        self.target = None
        self.non_targets = []
        self.strategy = strategy
        self.stance = stance
        self.run_away_factor = 0.2
        if self.stance == 'defensive':
            self.stay_away_distance = self.laser_range + 20
        else:
            self.stay_away_distance = 0

    def within_range(self, target):
        """Is this target within weapons range"""
        return self.distance_to(target) < self.laser_range

    def damage(self, points):
        """Inflict damage on this ship"""
        if self.shield > 1:
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
        self.shield = min(self.shield, ship_specs[self.ship_type]['shield'])

        # Shield recharge
        self.hp += self.hull_recharge
        self.hp = min(self.hp, ship_specs[self.ship_type]['hp'])

        # Choose the main target if it's within range, otherwise ask for secondary target
        if self.squad.main_target and self.within_range(self.squad.main_target):
            self.target = self.squad.main_target
        else:
            self.target = self.squad.secondary_target(self)

        # Compute target logic only if I have a target
        if self.target:

            # Compute my non targets
            self.non_targets = self.squad.adversaries.copy()
            self.non_targets.remove(self.target)

            # Move Towards (Attack)
            if self.distance_to(self.target) > self.laser_range/2.0:
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
        hull_health = min(self.hp / ship_specs[self.ship_type]['hp'] + 0.5, 1.0)
        hull_color = (self.color[0] * hull_health, self.color[1] * hull_health, self.color[2] * hull_health)
        self.display.draw_circle(hull_color, (self.x, self.y), self.radius, width=self.ship_width)
        self.display.draw_circle((30, 30, 30), (self.x, self.y), self.radius-self.ship_width, width=0)
        if self.low_health():
            self.display.draw_circle((240, 240, 240), (self.x, self.y), 3)

    def draw_dead(self):
        """Draw the Dead Ship Icon"""
        self.display.draw_circle((0, 0, 0), (self.x, self.y), self.radius)

    def draw_laser(self):
        """Draw the laser"""
        if self.target and self.distance_to(self.target) < self.laser_range:
            self.display.draw_line(self.color, (self.x, self.y), (self.target.x, self.target.y), width=self.laser_width)
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
        shield_health = self.shield * 255 / ship_specs[self.ship_type]['shield']
        shield_color = (shield_health, shield_health, shield_health)
        self.display.draw_circle(shield_color, (self.x, self.y), self.shield_radius, width=self.shield_width)


# Simple test of the Ship functionality
def test():
    """Test for Ship Class"""
    from space_bots import display_adapter

    # Create a fake universe (just for testing)
    class Universe:
        pass
    Universe.display = display_adapter.DisplayAdapter()

    # Create a fake squad (just for testing)
    class Squad:
        pass
    Squad.team = 'red'
    Squad.team_colors = {'red': (200, 80, 80)}

    # Create our ship
    my_ship = Ship(Universe, 100, 100, squad=Squad, ship_type='destroyer')

    # Register the Actor with the Display Adapter
    Universe.display.register_actor(my_ship)
    Universe.display.event_loop()


if __name__ == "__main__":
    test()
