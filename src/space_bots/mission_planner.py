"""MissionPlanner: Class for Mission Planning in Space Bots"""
import os
import json
import time
from queue import Queue

# Local Imports
from space_bots import squad
from space_bots.planet import Planet
from space_bots.ships import drone, miner, healer, tank, fighter
from space_bots.ships import zergling, ship


class MissionPlanner:
    """MissionPlanner: Class for the Mission Planning in Space Bots"""
    def __init__(self, universe):

        # Set up my internal attributes
        self.universe = universe
        self.mission_level = None
        self.current_mission = None
        self.test_squads = None
        self.test_squads_pos = (300, 500)
        self.zerg_pos = (1100, 700)
        self.mission_planet = None
        self.mission_begin_time = None
        self.event_queue = Queue()

        # Read in Mission Specifications
        file_path = os.path.join(os.path.dirname(__file__), 'missions/mission_specs.json')
        with open(file_path) as fp:
            self.mission_specs = json.load(fp)

    def set_mission(self, mission_level, test_squads=False):
        """Set a Specific Mission"""
        mission_name = f"mission_{mission_level}"
        self.current_mission = self.mission_specs[mission_name]

        # FIXME: Planets should be part of the mission specifications
        self.mission_planet = Planet(self.universe.game_engine, x=600, y=400)
        self.universe.add_planet(self.mission_planet)

        # Do we want some test squads for this mission?
        if test_squads:
            self.add_test_squads()

        # Set up the mission event queue
        for event in self.current_mission['event_sequence']:
            self.event_queue.put(event)

        # Set the Universe Text
        self.universe.current_text = self.current_mission['title']

    def buff_squads(self):
        self.universe.game_engine.restricted_announce('power_cord_d', None)
        self.universe.game_engine.restricted_announce('get_buffed')
        for squad in self.test_squads:
            squad.get_buffed()

    def add_zerg_squad(self, ship_type, num_ships, targeting, level=1):
        """Add a Zerg Squad to the mission"""
        x = self.zerg_pos[0]
        y = self.zerg_pos[1]
        zerg_squad = squad.Squad('zerg', 'bugs_are_cool', target_strategy=targeting)
        if ship_type == 'zergling':
            for _ in range(num_ships):
                zerg_squad.add_ship(zergling.Zergling(self.universe.game_engine, x=x, y=y, level=level))
        else:
            for _ in range(num_ships):
                zerg_squad.add_ship(ship.Ship(self.universe.game_engine, x=x, y=y, ship_type=ship_type, level=level))
        self.universe.add_squad(zerg_squad)

    def standard_zerg_pack(self, pack_size=1.0, targeting='nearest', level=1):
        """Add a predefined/diverse set of Zerg Squads to the mission"""
        pack = {
            'zergling': 5,
            'spitter': 2,
            'berserker': 1,
            'mega_bug': 0.25
        }
        for ship_type, count in pack.items():
            num_ships = int(count * pack_size)
            if num_ships:
                self.add_zerg_squad(ship_type, num_ships, targeting, level)

    def add_test_squads(self):
        """We can add 'earth' Squads to test the Mission balance/level/etc"""

        # Add out Test Squads
        self.test_squads = []
        for squad_info in self.current_mission['test_squads']:

            # Add Squad and Ships
            targeting = squad_info.get('targeting', 'threat')
            new_squad = squad.Squad('earth', squad_info['name'], target_strategy=targeting)
            for ship_info in squad_info['ships']:
                self._add_ship_to_test_squad(new_squad, ship_info['type'], ship_info['level'])
            self.test_squads.append(new_squad)

        # Add the Test Squads to the Universe
        for _squad in self.test_squads:
            self.universe.add_squad(_squad)

    def _set_focus_orders(self, source_name, target_name, focus_type, distance=None):
        """Internal: Get the current mission and pull out focus (protect or attack) orders"""

        # This code is a bit wonky, we want flexibility in protection/attack orders
        # So for the target we need to go through planets, squads and ships to see what they want

        # Get the source
        source = self._get_squad(source_name)

        # Get the target (planet, squad or ship)
        if target_name == 'planet':
            target = self.mission_planet
        else:
            # The Target might be a Squad
            target = self._get_squad(target_name)

            # Okay, maybe a ship within a squad
            if target is None:
                target = self._get_ship(target_name)

        # Now execute focus order
        if focus_type == 'protect':
            source.protect(target, distance)

    def _get_ship(self, ship_type):
        """Internal: Given a ship type get the ship with that type
           Note: For more than one ship this just returns the first one"""
        for _squad in self.test_squads:
            for _ship in _squad.ships:
                if _ship.ship_type == ship_type:
                    return _ship

    def _get_squad(self, squad_name):
        """Internal: Return the Squad class with the given squad_name"""
        for _squad in self.test_squads:
            if _squad.squad_name == squad_name:
                return _squad
        return None

    def _add_ship_to_test_squad(self, squad, ship_type, level):
        """Internal: Add a ship to our test Squad"""
        # FIXME: This should be a factory pattern or something better
        x = self.test_squads_pos[0]
        y = self.test_squads_pos[1]
        if ship_type == 'healer':
            squad.add_ship(healer.Healer(self.universe.game_engine, x=x, y=y, level=level))
        elif ship_type == 'tank':
            squad.add_ship(tank.Tank(self.universe.game_engine, x=x, y=y, level=level))
        elif ship_type == 'fighter':
            squad.add_ship(fighter.Fighter(self.universe.game_engine, x=x, y=y, level=level))
        elif ship_type == 'miner':
            squad.add_ship(miner.Miner(self.universe.game_engine, x=x, y=y, level=level))
        elif ship_type == 'drone':
            squad.add_ship(drone.Drone(self.universe.game_engine, x=x, y=y, level=level))

    def update(self):
        """Main Mission Planner Functionality"""
        if self.mission_begin_time is None:
            self.mission_begin_time = time.time()
            self.buff_squads()

        # If we have no more events in this mission just return
        if self.event_queue.empty():
            return

        # Go through this mission event sequence
        now = time.time()

        # Let's check the time on the next event (without popping)
        peek_event = self.event_queue.queue[0]

        # If the event is ready then get() it off the event queue and process
        if peek_event['time'] + self.mission_begin_time < now:
            event_info = self.event_queue.get()['event_info']

            # Add Squads
            if 'squad' in event_info:
                squad_info = event_info['squad']
                # Add a Standard Zerg Pack
                if squad_info['type'] == 'standard_zerg_pack':
                    self.standard_zerg_pack(squad_info['pack_size'], squad_info.get('targeting', 'nearest'),
                                            squad_info.get('level', 1))

                # Add an individual Squad
                else:
                    self.add_zerg_squad(squad_info['type'], squad_info['count'],
                                        squad_info.get('targeting', 'nearest'), squad_info.get('level', 1))

            # Protection Orders
            if 'protect' in event_info:
                for source, target_info in event_info['protect'].items():
                    target = target_info['target']
                    distance = target_info.get('distance', 150)
                    self._set_focus_orders(source, target, focus_type='protect', distance=distance)

            # Attack Target Orders
            if 'attack' in event_info:
                for source, target_info in event_info['attack'].items():
                    target = target_info['target']
                    self._set_focus_orders(source, target, focus_type='attack')

    def finalize(self):
        """Mission Planner Finalize"""
        print('Mission Planner Finalize...')


# Simple test of the MissionPlanner functionality
def test():
    """Test for MissionPlanner Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe

    # Create a universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Get the Universe Mission Planner
    my_mission = my_universe.mission_planner
    my_mission.set_mission(18, test_squads=True)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
