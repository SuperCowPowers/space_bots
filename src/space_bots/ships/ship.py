"""Ship: Class for the ships in Space Bots"""

# Local Imports
from space_bots import entity, force_utils
from space_bots.ships import ship_parameters, ship_state


class Ship(entity.Entity):
    """Ship: Class for the ships in Space Bots"""
    def __init__(self, game_engine, x=100, y=100, ship_type='fighter'):

        # Set my attributes
        self.squad = None
        self.team = None

        # Set my Ship Parameters, State, and Buffs
        self.ship_type = ship_type
        self.p = ship_parameters.ShipParameters(ship_type)
        self.s = ship_state.ShipState(ship_type)

        # Battle State/Reconnaissance
        self.battle_state = None

        # In combat indicator
        self.in_combat = False
        self.combat_timer = 0
        self.dead = False

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=self.p.mass, speed=self.p.speed,
                         collision_radius=self.p.collision_radius)

        # Hack
        if ship_type in ['scout', 'zergling']:
            self.force_damp = 0.999

    def set_battle_state(self, battle_state):
        self.battle_state = battle_state

    def squad_in_combat(self):
        return self.squad.in_combat if self.squad else False

    def within_range(self, target):
        """Is this target within weapons range"""
        return force_utils.distance_between(self, target) < self.p.laser_range

    def damage(self, points):
        """Inflict damage on this ship"""

        # You're in combat
        self.in_combat = True
        self.combat_timer = 100

        # Damage modifiers
        points *= self.p.damage_modifier  # FIXME should be state

        # Extra Shield Damage
        if points < self.s.extra_shield:
            self.s.extra_shield -= points
            return

        # We're into Shield (so explicitly set extra shield to 0)
        points -= self.s.extra_shield
        self.s.extra_shield = 0

        # Shield Damage
        if points < self.s.shield:
            self.s.shield -= points
            return

        # We're into Hull/HP (so explicitly set shield to 0)
        points -= self.s.shield
        self.s.shield = 0

        # Hull Damage
        self.s.hp -= points
        if self.s.hp <= 0:
            self.s.hp = 0
            self.dead = True

    def heal(self, points):
        """Heal any damage on this ship"""

        # Heal might cover some hull and some shield
        hull_damage = self.p.hp - self.s.hp
        if hull_damage:
            self.s.hp = min(self.s.hp + points, self.p.hp)
            points -= hull_damage

        # Now Shield
        if points > 0:
            self.s.shield = min(self.s.shield + points, self.p.shield)

    def health(self):
        return self.s.hp + self.s.shield  # Not counting self.s.extra_shield for now

    def health_percent(self):
        return self.health()/self.p.total_health

    def low_health(self):
        return self.health_percent() < 0.5

    def critical_health(self):
        return self.health_percent() < 0.2

    def is_dead(self):
        return self.dead

    def communicate(self):
        """Communicate with Squad or Team"""
        pass

    def general_ship_updates(self):
        """Update the general things associated with all ships"""
        # Shield recharge
        self.s.shield += self.p.shield_recharge
        self.s.shield = min(self.s.shield, self.p.shield)

        # Hull recharge
        self.s.hp += self.p.hull_recharge
        self.s.hp = min(self.s.hp, self.p.hp)

        # Combat logic
        self.combat_timer -= 1
        if self.combat_timer < 0:
            self.combat_timer = 0
            self.in_combat = False

    def general_targeting(self):
        """Targeting logic that's useful for most ships"""
        # Choose the main target if it's within range, otherwise ask for secondary target
        if self.squad:
            if self.squad.main_target and self.within_range(self.squad.main_target):
                self.s.target = self.squad.main_target
            else:
                self.s.target = self.squad.secondary_target(self)

        # Move towards primary target (even if it's not my current target)
        if self.squad.main_target:
            (dx, dy), (_, _) = force_utils.attraction_forces(self, self.squad.main_target, self.p.laser_range/1.2)
            self.force_x += dx
            self.force_y += dy

    def general_avoidance(self, factor=0.5):
        """Avoidance logic that's useful for most ships"""
        for enemy_ship in self.squad.adversaries:
            (dx, dy), (_, _) = force_utils.repulsion_forces(self, enemy_ship, rest_distance=self.p.keep_range)
            self.force_x += dx * factor
            self.force_y += dy * factor

    def update(self):
        """Update the Ship"""

        # General updates
        self.general_ship_updates()
        self.general_targeting()
        self.general_avoidance()

        # Now actually call the move command (which uses force/mass calc)
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_laser()
        self.draw_ship()
        self.draw_shield()
        self.draw_buffs()

    def draw_ship(self):
        """Draw the Ship Icon"""
        hull_health = min(self.s.hp / self.p.hp + 0.6, 1.0)
        hull_color = (self.p.color[0] * hull_health, self.p.color[1] * hull_health, self.p.color[2] * hull_health)
        self.game_engine.draw_circle((30, 30, 30), (self.x, self.y), self.p.radius, width=0)
        self.game_engine.draw_circle(hull_color, (self.x, self.y), self.p.radius, width=self.p.ship_width)

        # FIXME
        width = 1 if self.ship_type in ['scout', 'zergling'] else 0
        if self.low_health():
            self.game_engine.draw_circle((200, 200, 0), (self.x, self.y), 5, width=width)
        if self.critical_health():
            self.game_engine.draw_circle((240, 0, 0), (self.x, self.y), 5, width=width)

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
            shield_color = (shield_health/1.5, shield_health/1.5, shield_health/1.5)
        else:
            shield_color = (shield_health, shield_health, shield_health)
        self.game_engine.draw_circle(shield_color, (self.x, self.y), self.p.shield_radius, width=self.p.shield_width)

        # Do we have an extra shield?
        if self.s.extra_shield > 0:
            shield_health = 220 * self.s.extra_shield / 800 + 35  # FIXME: Hardcode
            shield_color = (shield_health/2, shield_health/2, shield_health)
            self.game_engine.draw_circle(shield_color, (self.x, self.y), self.p.shield_radius+4, width=3)

    def add_buff(self, buff):
        """Add a buff to this ship"""
        self.s.buffs.add(buff)

        # Buff effects
        effects = self.s.buff_info[buff]['effects']
        for attribute, value in effects.items():
            setattr(self.s, attribute, value)

        # FIXME: Do something with the timers

    def draw_buffs(self):
        """Draw any buffs we might have"""
        # Each buff gets a +2 radius :)
        buff_pos = self.p.shield_radius+8 if self.s.extra_shield else self.p.shield_radius+4
        for buff in self.s.buffs:
            # Is it a buff that we display?
            if self.s.buff_info[buff]['display']:
                color = self.s.buff_info[buff]['color']
                self.game_engine.draw_circle(color, (self.x, self.y), buff_pos, width=2)
                buff_pos += 2


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
