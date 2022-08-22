"""Ship: Class for the ships in Space Bots"""

# Local Imports
from space_bots import entity, ship_parameters, ship_state, force_utils


class Ship(entity.Entity):
    """Ship: Class for the ships in Space Bots"""
    def __init__(self, game_engine, x=100, y=100, ship_type='fighter'):

        # Set my attributes
        self.squad = None
        self.team = None

        # Set my Ship Parameters and State
        self.ship_type = ship_type
        self.p = ship_parameters.ShipParameters(ship_type)
        self.s = ship_state.ShipState(ship_type)

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=self.p.mass, speed=self.p.speed,
                         collision_radius=self.p.collision_radius)

    def within_range(self, target):
        """Is this target within weapons range"""
        return force_utils.distance_between(self, target) < self.p.laser_range

    def damage(self, points):
        """Inflict damage on this ship"""

        # Shield Damage
        if points < self.s.shield:
            self.s.shield -= points

        # Shield and Hull Damage
        else:
            points -= self.s.shield
            self.s.shield = 0
            self.s.hp = max(self.s.hp - points, 0)

    def health(self):
        return self.s.hp + self.s.shield

    def health_percent(self):
        return self.health()/self.p.total_health

    def low_health(self):
        return self.health_percent() < 0.5

    def critical_health(self):
        return self.health_percent() < 0.2

    def is_dead(self):
        return self.s.hp == 0

    def position_delta(self, target, fraction=1.0):
        dx = (target[0] - self.x) * fraction
        dy = (target[1] - self.y) * fraction
        return dx, dy

    def communicate(self):
        """Communicate with Squad or Team"""
        pass

    def update(self):
        """Update the Ship"""

        # Shield recharge
        self.s.shield += self.p.shield_recharge
        self.s.shield = min(self.s.shield, self.p.shield)

        # Hull recharge
        self.s.hp += self.p.hull_recharge
        self.s.hp = min(self.s.hp, self.p.hp)

        # Choose the main target if it's within range, otherwise ask for secondary target
        if self.squad and self.ship_type not in ['healer', 'miner']:
            if self.squad.main_target and self.within_range(self.squad.main_target):
                self.s.target = self.squad.main_target
            else:
                self.s.target = self.squad.secondary_target(self)

        # Compute my non targets
        self.s.non_targets = self.squad.adversaries.copy()

        # Compute target logic only if I have a target
        if self.s.target:
            # Remove target from the non targets list
            self.s.non_targets.remove(self.s.target)

            # Move Towards (Attack)
            (dx, dy), (_, _) = force_utils.attraction_forces(self, self.s.target, self.p.laser_range/1.5)
            self.force_x += dx
            self.force_y += dy

        # Avoidance of Non Targets
        # This will be different for healer/miners
        for other_ship in self.s.non_targets:
            (dx, dy), (_, _) = force_utils.repulsion_forces(self, other_ship, rest_distance=self.p.keep_range)
            self.force_x += dx * 10.0
            self.force_y += dy * 10.0

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_laser()
        self.draw_ship()
        self.draw_shield()

    def draw_ship(self):
        """Draw the Ship Icon"""
        hull_health = min(self.s.hp / self.p.hp + 0.6, 1.0)
        hull_color = (self.p.color[0] * hull_health, self.p.color[1] * hull_health, self.p.color[2] * hull_health)
        self.game_engine.draw_circle((30, 30, 30), (self.x, self.y), self.p.radius, width=0)
        self.game_engine.draw_circle(hull_color, (self.x, self.y), self.p.radius, width=self.p.ship_width)
        if self.low_health():
            self.game_engine.draw_circle((200, 200, 0), (self.x, self.y), 3)
        if self.critical_health():
            self.game_engine.draw_circle((240, 0, 0), (self.x, self.y), 3)

    def draw_dead(self):
        """Draw the Dead Ship Icon"""
        self.game_engine.draw_circle((0, 0, 0), (self.x, self.y), self.p.radius)

    def draw_laser(self):
        """Draw the laser"""
        if self.s.target and force_utils.distance_between(self, self.s.target) < self.p.laser_range:
            self.game_engine.draw_line(self.p.color, (self.x, self.y), (self.s.target.x, self.s.target.y), width=self.p.laser_width)
            self.s.target.damage(self.p.laser_damage)

    def draw_shield(self):
        """Draw the Shield"""
        shield_health = 220 * self.s.shield / self.p.shield + 35
        if self.team == 'pirate':
            shield_color = (shield_health/4, shield_health/4, shield_health/4)
        else:
            shield_color = (shield_health, shield_health, shield_health)
        self.game_engine.draw_circle(shield_color, (self.x, self.y), self.p.shield_radius, width=self.p.shield_width)


# Simple test of the Ship functionality
def test():
    """Test for Ship Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create two ships (one more massive than another
    heavy_ship = Ship(my_game_engine, 100, 100, ship_type='shielder')
    light_ship = Ship(my_game_engine, 100, 200, ship_type='healer')
    my_universe.add_ship(heavy_ship)
    my_universe.add_ship(light_ship)

    # Give the ship a push and do some damage
    heavy_ship.force_x = 1000
    heavy_ship.force_y = 500
    heavy_ship.damage(500)

    # Give the healer a push (should move further)
    light_ship.force_x = 1000
    light_ship.force_y = 500

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
