"""Squad: Class for the squads in Space Bots"""

# Note: This class manages a LOT of stuff right now
#     Future breakouts
#     - Targeting Strategy
#     - Stance/Positioning Strategy
#     - etc...
from random import choice
import statistics
import math

# Local Imports
from space_bots import force_utils, battle_state


class Squad:
    """Squad: Class for the Squads in Space Bots"""
    def __init__(self, team, squad_name, target_strategy='nearest', stance='defensive'):

        # Set my attributes
        self.team = team
        self.squad_name = squad_name
        self.adversaries = None
        self.target_strategy = target_strategy
        self.main_target = None
        self.stance = stance

        # Squad position will be centroid of the Squad
        self.x = 0
        self.y = 0

        # The Ships in this Squad
        self.ships = []

        # Keep info/stats on my adversaries (populated in update)
        self.adversaries = None
        self.ship_health = None
        self.ship_distance = None
        self.ship_mass = None
        self.ship_threat = None

        # Capture Sticky Targets
        self.sticky_targets = {}

        # Protection Asset
        self.protection_asset = None

        # Battle State/Reconnaissance
        self.battle_state = None
        self.in_combat = False
        self.combat_timer = 0
        self.combat_status_change = False

    def add_ship(self, ship):
        """Add a Ship to this Squad"""
        ship.team = self.team
        ship.squad = self
        self.ships.append(ship)

    def set_battle_state(self, battle_state):
        self.battle_state = battle_state
        for ship in self.ships:
            ship.set_battle_state(battle_state)

    def set_combat_status(self, combat):

        # FIXME: We should have 'lag' vars in a utility class
        if combat == self.in_combat:
            self.combat_status_change = False
            return
        else:
            # Change in state, lets set the timer
            if combat:
                self.combat_timer = 300
                self.combat_status_change = True
                self.in_combat = True
            else:
                self.combat_timer -= 1
                if self.combat_timer == 0:
                    self.combat_status_change = True
                    self.in_combat = False

    def protect(self, asset):
        """Tell the Squad to protect a planet, squad or ship (asset)"""
        self.stance = 'protect'
        self.protection_asset = asset

    def communicate(self):
        """Squad Communication"""
        if not self.ships:
            return
        if self.combat_status_change:
            if self.in_combat:
                print(f'{self.team}:{self.squad_name}: Get Pumped...')
            else:
                print(f'{self.team}:{self.squad_name}: Whew, out of combat...')

    def update(self):
        """Update the Squad"""

        # Remove any dead ships
        self.ships = [s for s in self.ships if not s.is_dead()]

        # Are any of my ships in combat?
        self.set_combat_status(any([s.in_combat for s in self.ships]))

        # Get my adversaries
        self.adversaries = self.battle_state.adversary_ships(self)

        # Compute health, mass, and threat (mass*1/distance)
        self.ship_health = self.lowest_health()
        self.ship_distance = self.distance_from_squad()
        self.ship_mass = self.highest_mass()
        self.ship_threat = self.highest_threat()

        # Compute information about the squad
        self.x, self.y = self.compute_centroid()
        self.main_target = self.compute_main_target()

        # Squad Movement: Group up
        for _ship in self.ships:
            (_, _), (dx, dy) = force_utils.attraction_forces(self, _ship, 60)
            _ship.force_x += dx
            _ship.force_y += dy

        # Protect Stance
        if self.stance == 'protect':
            for _ship in self.ships:
                (_, _), (dx, dy) = force_utils.attraction_forces(self.protection_asset, _ship, 150)
                _ship.force_x += dx
                _ship.force_y += dy

        # Update each ship
        for _ship in self.ships:
            _ship.update()

    def draw(self):
        """Draw the entire squad"""
        for _ship in self.ships:
            _ship.draw()

    def compute_centroid(self, mass_based=True):
        if not self.ships:
            return 0, 0
        if not mass_based:
            x_centroid = statistics.fmean([s.x for s in self.ships])
            y_centroid = statistics.fmean([s.y for s in self.ships])
            return x_centroid, y_centroid
        else:
            total_mass = sum([s.mass for s in self.ships])
            x_centroid = sum([s.x * s.mass for s in self.ships])
            y_centroid = sum([s.y * s.mass for s in self.ships])
            return x_centroid/total_mass, y_centroid/total_mass

    def lowest_health(self):
        ship_health = [(s, s.health()) for s in self.adversaries]
        ship_health.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_health]

    def highest_mass(self):
        ship_mass = [(s, s.mass) for s in self.adversaries]
        ship_mass.sort(key=lambda tup: -tup[1])
        return [s[0] for s in ship_mass]

    def highest_threat(self):
        ship_threat = [(s, s.p.threat) for s in self.adversaries]
        ship_threat.sort(key=lambda tup: -tup[1])
        return [s[0] for s in ship_threat]

    def distance_from_squad(self):
        squad_distance = [(s, force_utils.distance_between(self, s)) for s in self.adversaries]
        squad_distance.sort(key=lambda tup: tup[1])
        return [s[0] for s in squad_distance]

    def distance_from_ship(self, ship):
        ship_distance = [(s, force_utils.distance_between(ship, s)) for s in self.adversaries]
        ship_distance.sort(key=lambda tup: tup[1])
        return [s[0] for s in ship_distance]

    def _distance_centroid(self, target):
        dx = self.x - target.x
        dy = self.y - target.y
        return dx, dy

    def distance_to(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def compute_main_target(self):
        """Select the squads main target based on a Strategy"""
        try:
            if self.target_strategy == 'low_health':
                return self.ship_health[0]
            if self.target_strategy == 'nearest':
                return self.ship_distance[0]
            if self.target_strategy == 'threat':
                return self.ship_threat[0]
            if self.target_strategy == 'random' or 'no_target':
                return None  # Special Logic for Random
        except IndexError:
            return None

    def secondary_target(self, my_ship):
        """A ship might ask for a secondary target"""
        try:
            if self.target_strategy == 'low_health':
                return self.get_sticky_target(my_ship, self.ship_health[1:4])
            if self.target_strategy == 'nearest':
                return self.distance_from_ship(my_ship)[0]
            if self.target_strategy == 'threat':
                return self.distance_from_ship(my_ship)[0]
            if self.target_strategy == 'random':
                return self.get_sticky_target(my_ship, self.adversaries)
            if self.target_strategy == 'no_target':
                return None
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
    from space_bots import game_engine_adapter
    from space_bots.ships import ship, miner, healer
    from space_bots.universe import Universe

    # Create a universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create our Squad
    my_squad = Squad(team='player', squad_name='roughnecks', target_strategy='threat')
    healer = healer.Healer(my_game_engine, 200, 200)
    my_squad.add_ship(healer)
    shielder = ship.Ship(my_game_engine, 300, 300, ship_type='shielder')
    my_squad.add_ship(shielder)
    fighter = ship.Ship(my_game_engine, 100, 300, ship_type='fighter')
    my_squad.add_ship(fighter)
    miner = miner.Miner(my_game_engine, 100, 100)
    my_squad.add_ship(miner)

    # Create a Pirate Squad (who doesn't want to be a pirate?)
    pirate_squad = Squad(team='pirate', squad_name='xenos')
    healer = ship.Ship(my_game_engine, 600, 600, ship_type='healer')
    pirate_squad.add_ship(healer)
    shielder = ship.Ship(my_game_engine, 700, 700, ship_type='shielder')
    pirate_squad.add_ship(shielder)
    fighter = ship.Ship(my_game_engine, 700, 700, ship_type='fighter')
    pirate_squad.add_ship(fighter)

    # Give our Squads the Battle State (universal in this case)
    my_battle_state = battle_state.BattleState(my_universe)
    my_squad.set_battle_state(my_battle_state)
    pirate_squad.set_battle_state(my_battle_state)

    # Add both Squads to the Universe
    my_universe.add_squad(my_squad)
    my_universe.add_squad(pirate_squad)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
