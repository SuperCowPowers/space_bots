"""Squad: Class for the squads in Space Bots"""

# Note: This class manages a LOT of stuff right now
#     Future breakouts
#     - Targeting Strategy
#     - Stance/Positioning Strategy
#     - etc...
from random import choice
import statistics
import math
from queue import SimpleQueue

# Local Imports
from space_bots.utils import force_utils


class Squad:
    """Squad: Class for the Squads in Space Bots"""
    def __init__(self, team, squad_name, target_strategy='nearest'):

        # Set my attributes
        self.game_engine = None
        self.team = team
        self.squad_name = squad_name
        self.adversaries = None
        self.target_strategy = target_strategy
        self.main_target = None

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

        # Communications Message Queues
        self.announcer_messages = SimpleQueue()

        # Capture Sticky Targets
        self.sticky_targets = {}

        # Protection Asset
        self.protection_asset = None
        self.protection_distance = 150

        # Battle State/Reconnaissance
        self.battle_info = None
        self.in_combat = False
        self.first_combat = True
        self.combat_timer = 0
        self.combat_status_change = False
        self.total_zenite = 0
        self.total_damage = 0
        self.buff_manager = None

    def add_ship(self, ship):
        """Add a Ship to this Squad"""
        ship.team = self.team
        ship.squad = self
        ship.battle_info = self.battle_info
        self.ships.append(ship)

    def set_battle_info(self, battle_info):
        """Someone has given us battle info/reconnaissance"""
        self.battle_info = battle_info
        for ship in self.ships:
            ship.set_battle_info(battle_info)

    def set_buff_manager(self, buffs):
        self.buff_manager = buffs
        for ship in self.ships:
            ship.buff_manager = buffs

        # Now add squad buffs
        self.add_squad_buffs()

    def add_squad_buffs(self):
        """Now add squad buffs"""
        fighters = [ship for ship in self.ships if ship.ship_type == 'fighter']
        for ship in fighters:
            self.buff_manager.apply('first_strike', ship)

    def set_combat_status(self, combat):

        # FIXME: We should have 'lag' vars in a utility class
        if combat == self.in_combat:
            self.combat_status_change = False
            return
        else:
            # Change in state, lets set the timer
            if combat:
                self.combat_timer = 200
                self.combat_status_change = True
                self.in_combat = True
            else:
                self.combat_timer -= 1
                if self.combat_timer == 0:
                    self.combat_status_change = True
                    self.in_combat = False

    def protect(self, asset, distance=150):
        """Tell the Squad to protect a planet, squad or a ship (asset)"""
        self.protection_asset = asset
        self.protection_distance = distance

    def communicate(self, comms):
        """Squad Communication"""

        # FIXME:
        if self.team != 'earth':
            return

        # Squad level communication
        if self.combat_status_change:
            if self.in_combat and self.first_combat and self.squad_name == 'roughnecks':
                # comms.announce('lets_rock', 'squad_leader_1')
                self.first_combat = False

        # Squad Zenite Extracted and Damage Taken
        zenite_market_price = 100
        repair_unit_cost = 50
        zenite_worth = self.total_zenite*zenite_market_price / 1000.0
        repair_cost = self.total_damage*repair_unit_cost / 1000.0
        zenite = f'ZeNite@Market: ${zenite_worth:.1f}k'
        repairs = f' - Repair Cost: ${repair_cost:.1f}k'
        net = zenite_worth - repair_cost
        total = f' = ${net:.1f}k'
        display_text = zenite + repairs + total
        comms.display('mission_info', display_text)

        # Also communicate any queued announcer messages
        while not self.announcer_messages.empty():
            comms.announce(self.announcer_messages.get())

        # Let each ship communicate
        for ship in self.ships:
            ship.communicate(comms)

    def update(self):
        """Update the Squad"""

        # Remove any dead ships
        self.ships = [s for s in self.ships if not s.is_dead()]

        # Are any of my ships in combat?
        self.set_combat_status(any([s.in_combat for s in self.ships]))

        # Get my adversaries
        self.adversaries = self.battle_info.adversary_ships(self)

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
            (_, _), (dx, dy) = force_utils.attraction_forces(self, _ship, 120)
            _ship.force_x += dx
            _ship.force_y += dy

        # Protecting an Asset
        if self.protection_asset:
            for _ship in self.ships:
                (_, _), (dx, dy) = force_utils.attraction_forces(self.protection_asset, _ship, self.protection_distance)
                _ship.force_x += dx
                _ship.force_y += dy

        # Update each ship
        for _ship in self.ships:
            _ship.update()

        # How ZeNite extracted and Damage Taken (Repairs)
        self.total_zenite = sum([m.mining_yield for m in self.ships if m.ship_type == 'miner'])
        self.total_damage = sum([s.damage_taken for s in self.ships])

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
        ship_mass.sort(key=lambda tup: tup[1], reverse=True)
        return [s[0] for s in ship_mass]

    def highest_threat(self):
        ship_threat = [(s, s.p.threat) for s in self.adversaries]
        ship_threat.sort(key=lambda tup: tup[1], reverse=True)
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
    from space_bots.ships import ship, miner, healer, tank, fighter
    from space_bots.universe import Universe

    # Create a universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create our Squad
    my_squad = Squad('earth', 'roughnecks', target_strategy='threat')
    my_squad.add_ship(healer.Healer(my_game_engine, 600, 400, level=2))
    my_squad.add_ship(tank.Tank(my_game_engine, 600, 400))
    my_squad.add_ship(fighter.Fighter(my_game_engine, 600, 400))
    my_squad.add_ship(miner.Miner(my_game_engine, 600, 400))

    # Create a Pirate Squad (who doesn't want to be a pirate?)
    pirate_squad = Squad('xenos', 'pirates', target_strategy='nearest')
    pirate_squad.add_ship(ship.Ship(my_game_engine, 1200, 700, ship_type='spitter'))
    pirate_squad.add_ship(ship.Ship(my_game_engine, 1200, 700, ship_type='spitter'))
    pirate_squad.add_ship(ship.Ship(my_game_engine, 1200, 700, ship_type='berserker'))
    pirate_squad.add_ship(ship.Ship(my_game_engine, 1200, 700, ship_type='berserker'))

    # Add a Zerg squad
    zerg_squad = Squad('xenos', 'zerg me', target_strategy='low_health')
    for _ in range(10):
        zerg_squad.add_ship(ship.Ship(my_game_engine, 1200, 700, ship_type='zergling'))

    # Add all Squads to the Universe
    my_universe.add_squad(zerg_squad)
    my_universe.add_squad(pirate_squad)
    my_universe.add_squad(my_squad)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
