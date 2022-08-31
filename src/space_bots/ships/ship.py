"""Ship: Class for the ships in Space Bots"""
from queue import SimpleQueue

# Local Imports
from space_bots import entity
from space_bots.utils import force_utils
from space_bots.ships import ship_parameters, ship_state


class Ship(entity.Entity):
    """Ship: Class for the ships in Space Bots"""
    def __init__(self, game_engine, x=500, y=500, ship_type='fighter', level=1):

        # Set my attributes
        self.squad = None
        self.team = None

        # Set my Ship Parameters, State, and Buffs
        self.ship_type = ship_type
        self.p = ship_parameters.ShipParameters(ship_type)
        self.s = ship_state.ShipState(ship_type)
        self.level = level

        # General ship adjustments
        self.p.laser_damage *= self.level

        # Battle State/Reconnaissance
        self.battle_info = None
        self.self_buffs = []
        self.squad_buffs = []
        self.buff_manager = None

        # Combat indicators and vars
        self.first_strike = False
        self.in_combat = False
        self.combat_timer = 0
        self.dead = False
        self.low_health_announced = False
        self.death_announced = False
        self.damage_done = 0
        self.damage_taken = 0
        self.current_laser_target = None
        self.new_laser_target = False

        # Communications Message Queues
        self.announcer_messages = SimpleQueue()

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, mass=self.p.mass, speed=self.p.speed,
                         collision_radius=self.p.collision_radius)

    def set_battle_info(self, battle_info):
        self.battle_info = battle_info

    def squad_in_combat(self):
        return self.squad.in_combat if self.squad else False

    def within_range(self, target):
        """Is this target within weapons range"""
        return force_utils.distance_between(self, target) < self.p.laser_range

    def damage(self, points):
        """Inflict damage on this ship"""

        # You're in combat
        self.in_combat = True
        self.combat_timer = 200

        # Damage modifiers
        points *= self.p.incoming_damage_modifier
        self.damage_taken += points

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
        return self.s.hp+self.s.shield

    def health_percent(self):
        return self.health()/(self.p.hp+self.p.shield)

    def medium_health(self):
        return self.health_percent() < 0.5

    def low_health(self):
        return self.health_percent() < 0.35

    def critical_health(self):
        return self.health_percent() < 0.2

    def is_dead(self):
        return self.dead

    def communicate(self, comms):
        """Communicate with Squad or Team"""
        # Only earth does all this communication
        if self.team == 'earth':
            if self.health_percent() < 0.5 and not self.low_health_announced:
                comms.announce(f"{self.ship_type}_low")
                self.low_health_announced = True
            if self.is_dead() and not self.death_announced:
                comms.announce('uff', None)
                comms.announce(f"{self.ship_type}_down")
                self.death_announced = True
            if self.current_laser_target and self.new_laser_target:
                comms.play_sound('laser')
                self.new_laser_target = False

        # Also communicate any queued announcer messages
        while not self.announcer_messages.empty():
            comms.announce(self.announcer_messages.get())

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
        if self.squad.main_target and self.within_range(self.squad.main_target):
            self.s.target = self.squad.main_target
        else:
            self.s.target = self.squad.secondary_target(self)

        # Move towards primary target (even if it's not my current target)
        if self.squad.main_target:
            (dx, dy), (_, _) = force_utils.attraction_forces(self, self.squad.main_target, self.p.laser_range/1.2)
            self.force_x += dx * 0.5
            self.force_y += dy * 0.5

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

        # Health Indicator
        # FIXME
        width = 1 if self.ship_type in ['scout', 'zergling'] else 0
        health_indicator_radius = int(max(self.p.radius/3, 3))
        if self.critical_health():
            self.game_engine.draw_circle((240, 20, 20), (self.x, self.y), health_indicator_radius, width=width)
        elif self.low_health():
            self.game_engine.draw_circle((220, 110, 20), (self.x, self.y), health_indicator_radius, width=width)
        elif self.medium_health():
            self.game_engine.draw_circle((200, 200, 20), (self.x, self.y), health_indicator_radius, width=width)
        elif self.health_percent() < 0.7:
            self.game_engine.draw_circle((100, 100, 10), (self.x, self.y), health_indicator_radius, width=width)

        # Level Pips
        if self.ship_type not in ['scout', 'zergling']:
            pip_y = self.y-self.p.radius
            pip_x = self.x+self.p.radius
            if self.level > 1:
                for _ in range(self.level):
                    self.game_engine.draw_circle(self.p.color, (pip_x, pip_y), 3, width=0)
                    pip_x += 5

    def draw_dead(self):
        """Draw the Dead Ship Icon"""
        self.game_engine.draw_circle((0, 0, 0), (self.x, self.y), self.p.radius)

    def draw_laser(self):
        """Draw the laser"""
        if self.s.target and force_utils.distance_between(self, self.s.target) < self.p.laser_range:
            self.first_strike = False

            # Track if new target
            if self.s.target != self.current_laser_target:
                self.current_laser_target = self.s.target
                self.new_laser_target = True

            # Draw the laser
            self.game_engine.draw_line(self.p.color, (self.x, self.y), (self.s.target.x, self.s.target.y), width=self.p.laser_width)

            # Do the Damage
            self.s.target.damage(self.p.laser_damage)
            self.damage_done += self.p.laser_damage

    def draw_shield(self):
        """Draw the Shield"""
        shield_health = min(220 * self.s.shield / self.p.shield + 35, 255)
        if self.team != 'earth':
            shield_color = (shield_health/2, shield_health/2, shield_health/2)
        else:
            shield_color = (shield_health, shield_health, shield_health)
        self.game_engine.draw_circle(shield_color, (self.x, self.y), self.p.shield_radius, width=self.p.shield_width)

    def add_buff(self, buff):
        """Any buff goes to the buff manager who manages the application and expiration of buffs"""
        self.buff_manager.apply(buff, self)

    def draw_buffs(self):
        """Draw any buffs we might have"""
        # Each buff gets a +2 radius :)
        buff_pos = self.p.shield_radius+2
        for buff in self.buff_manager.get_visible_buffs(self):
            color = buff['color']
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
    heavy_ship = Ship(my_game_engine, 300, 300, ship_type='tank')
    light_ship = Ship(my_game_engine, 400, 300, ship_type='healer')
    my_universe.add_ship(heavy_ship, team='earth')
    my_universe.add_ship(light_ship, team='earth')

    # Give the ship a push and do some damage
    heavy_ship.force_x = 10000
    heavy_ship.force_y = 5000
    heavy_ship.damage(500)

    # Give the healer a push
    light_ship.force_x = 1000
    light_ship.force_y = 500

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
