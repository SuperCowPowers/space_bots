"""Squad: Class for the squads in Space Bots"""

# Note: This class manages a LOT of stuff right now
#     Future breakouts
#     - Targeting Strategy
#     - Stance/Positioning Strategy
#     - etc...
from random import choice
import statistics
import math


class Squad:
    """Squad: Class for the Squads in Space Bots"""
    def __init__(self, team='player', target_strategy='random', stance='defensive'):

        # Set my attributes
        self.team = team
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

    def add_ship(self, ship):
        """Add a Ship to this Squad"""
        ship.team = self.team
        ship.squad = self
        self.ships.append(ship)

    def give_battle_state(self, battle_state):
        self.battle_state = battle_state

    def adversary_ships(self):
        """Ask the battle state for ships not on my team"""
        return [s for s in self.battle_state.all_ships if s.team != self.team]

    def protect(self, asset):
        """Tell the Squad to protect a planet, squad or ship (asset)"""
        self.stance = 'protect'
        self.protection_asset = asset

    def communicate(self):
        """Squad Communication"""
        pass

    def update(self):
        """Update the Squad"""

        # Remove any dead ships
        self.ships = [s for s in self.ships if not s.is_dead()]

        # Get my adversaries
        self.adversaries = self.adversary_ships()

        # Compute health, mass, and threat (mass*1/distance)
        self.ship_health = self.lowest_health()
        self.ship_distance = self.distance_from_squad()
        self.ship_mass = self.highest_mass()
        self.ship_threat = self.highest_threat()

        # Compute information about the squad
        self.x, self.y = self.compute_centroid()
        self.main_target = self.compute_main_target()

        # Squad Movement: Group up
        if self.stance in ['defensive', 'protect']:
            for _ship in self.ships:
                distance = _ship.distance_to(self)
                delta = _ship.position_delta((self.x, self.y), .05)
                # Only add force if we're kinda far away
                if distance > _ship.collision_radius * 8:
                    _ship.force_x += delta[0]
                    _ship.force_y += delta[1]
                elif distance < _ship.collision_radius * 3:
                    print('too close...')
                    _ship.force_x -= delta[0]
                    _ship.force_y -= delta[1]

        # Protect Stance
        if self.stance == 'protect':
            for _ship in self.ships:
                distance = _ship.distance_to(self.protection_asset)
                # Only add force if we're kinda far away
                if distance > _ship.collision_radius * 8:
                    delta = _ship.position_delta((self.protection_asset.x, self.protection_asset.y), .01)
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

    def highest_mass(self):
        ship_mass = [(s, s.mass) for s in self.adversaries]
        ship_mass.sort(key=lambda tup: -tup[1])
        return [s[0] for s in ship_mass]

    def highest_threat(self):
        threat_list = []
        for s in self.adversaries:
            dist = self.distance_to(s)
            damage = s.p.laser_damage
            threat_list.append((s, damage/dist))
            threat_list.sort(key=lambda tup: -tup[1])
        return [s[0] for s in threat_list]

    def distance_from_squad(self):
        squad_distance = [(s, self.distance_to(s)) for s in self.adversaries]
        squad_distance.sort(key=lambda tup: tup[1])
        return [s[0] for s in squad_distance]

    def distance_from_ship(self, ship):
        ship_distance = [(s, ship.distance_to(s)) for s in self.adversaries]
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
    from space_bots import game_engine_adapter, ship
    from space_bots.universe import Universe

    # Create a universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create our Squad
    my_squad = Squad(team='player')
    miner = ship.Ship(my_game_engine, 100, 100, ship_type='miner')
    my_squad.add_ship(miner)
    healer = ship.Ship(my_game_engine, 200, 200, ship_type='healer')
    my_squad.add_ship(healer)
    shielder = ship.Ship(my_game_engine, 300, 300, ship_type='shielder')
    my_squad.add_ship(shielder)
    fighter = ship.Ship(my_game_engine, 100, 300, ship_type='fighter')
    my_squad.add_ship(fighter)

    # Create a Pirate Squad (who doesn't want to be a pirate?)
    pirate_squad = Squad(team='pirate')
    miner = ship.Ship(my_game_engine, 500, 500, ship_type='miner')
    pirate_squad.add_ship(miner)
    healer = ship.Ship(my_game_engine, 600, 600, ship_type='healer')
    pirate_squad.add_ship(healer)
    shielder = ship.Ship(my_game_engine, 700, 700, ship_type='shielder')
    pirate_squad.add_ship(shielder)
    fighter = ship.Ship(my_game_engine, 500, 700, ship_type='fighter')
    pirate_squad.add_ship(fighter)

    # Give our Squads the Battle State (universal in this case)
    my_squad.give_battle_state(my_universe)
    pirate_squad.give_battle_state(my_universe)

    # Add both Squads to the Universe
    my_universe.add_squad(my_squad)
    my_universe.add_squad(pirate_squad)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
