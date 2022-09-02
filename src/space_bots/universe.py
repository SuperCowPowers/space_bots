"""Universe: Class that contains all the stuff"""
import time
import string
from random import randint, choice

# Local Imports
from space_bots import comms, battle_state, mission_planner
from space_bots.squad import Squad
from space_bots.utils import force_utils, buff_manager


class Universe:
    """Universe: Class that contains all the stuff"""

    # Note: Maybe refactor/rethink how this class should be used later
    #      - Collision Detection should be a separate class

    def __init__(self, width=1600, height=1000, announcements=True):
        """Initialize the Universe class"""
        self.game_engine = None
        self.announcements = announcements
        if announcements:
            self.time_slow = 0.0  # FIXME
        else:
            self.time_slow = 0
        self.pad = 150
        self.width = width
        self.height = height
        self.planets = []
        self.squads = []
        self.all_ships = []
        self.torps = []
        self.is_finalized = False

        self.initial_count_down = False
        self.wave_over = False
        self.current_text = None
        self.squads_buffed = False

        # Universal Battle Info and Buff Manager
        self.battle_info = battle_state.BattleState(self, scanner_range=1000)
        self.buffs = buff_manager.BuffManager()

        # Communication Channels
        self.comms = comms.Comms()

        # Mission Planner
        self.mission_planner = mission_planner.MissionPlanner(self)

    def finalize(self):
        """Tasks to do after initial universe setup"""
        print('Universe Finalize...')

        # We need a list of individual ships for collision detections
        self.all_ships = [ship for _squad in self.squads for ship in _squad.ships]

        # Make sure all entities are in a reasonable starting position
        self._space_out_planets()
        force_utils.resolve_coincident(self.all_ships)

        # Mission Planner Finalize
        self.mission_planner.finalize()

        # Start up the background music
        self.game_engine.play_background_music()

        # Put a couple of announcements into the comms
        # self.comms.announce('lets_rumble', voice='male')
        # self.comms.announce('great_match', voice='female')

        # All done setting up
        self.is_finalized = True

    def set_game_engine(self, game_engine):
        print('Universe: set_game_engine...')
        self.game_engine = game_engine

    def get_comms(self):
        return self.comms

    def add_planet(self, planet):
        """Add a Planet to the Universe"""
        self.planets.append(planet)

    def add_squad(self, squad):
        """Add a Squad to the Universe"""

        # Get Squad ready for Life in the Universe
        squad.game_engine = self.game_engine
        squad.set_battle_info(self.battle_info)
        squad.set_buff_manager(self.buffs)
        force_utils.resolve_coincident(squad.ships)

        # Add the Squad and update the Universal State
        self.squads.append(squad)
        self.all_ships = [ship for _squad in self.squads for ship in _squad.ships]

    @staticmethod
    def gen_squad_name():
        return 'solo_' + ''.join([choice(string.ascii_letters) for _ in range(4)])

    def add_ship(self, ship, team):
        """Add an Individual Ship to the Universe"""
        # Note: Design Choice to Make ALL ships be in squad
        #       Good? Bad? Not sure but it simplifies code
        squad = Squad(team=team, squad_name=self.gen_squad_name(), target_strategy='nearest')
        squad.add_ship(ship)
        self.add_squad(squad)

    def in_combat(self):
        return any([s.in_combat for s in self.squads])

    def buff_squads(self):
        self.game_engine.restricted_announce('power_cord_d', None)
        self.game_engine.restricted_announce('get_buffed')
        for squad in self.squads:
            squad.get_buffed()
        self.squads_buffed = True

    def communicate(self):
        """Let all the entities in the Universe communicate"""

        # Play announcements
        if self.announcements:
            for info in self.comms.get_messages('announcements'):
                if self.game_engine.restricted_announce(info['voice_line'], info['voice']):
                    self.time_slow = 0.2

        # Play sounds
        for sound_name in self.comms.get_messages('sounds'):
            self.game_engine.restricted_play_sound(sound_name)

        # Display info/stats
        for display_text in self.comms.get_messages('display'):
            self.current_text = display_text

        # Give the sound queue some cycles
        self.game_engine.play_sound_queue()

        # Have all the squads communicate
        for squad in self.squads:
            squad.communicate(self.comms)

    def update(self):
        """Let all the entities in the Universe update themselves"""

        # No one is going to remember to call finalize, so call it here
        if not self.is_finalized:
            self.finalize()

        # Mission Planner Update
        self.mission_planner.update()

        # FIXME: Buffs
        if self.in_combat() and not self.squads_buffed:
            print('Buffing Squads...')
            self.buff_squads()

        # Let check Squad Status
        for squad in self.squads.copy():  # Copy so we can remove from the actual list
            if squad.all_dead():
                squad.pre_delete()
                self.squads.remove(squad)

        # Build all ships list from remaining squads
        self.all_ships = []
        for squad in self.squads:
            self.all_ships += squad.ships

        # Build torps list from ships
        self.torps = []
        for ship in self.all_ships:
            self.torps += ship.torps

        # Now run collision detection
        self.collision_detection()

        # Update/Manage the buffs for all the ships
        self.buffs.update()

        # Now update all the Planets in the Universe
        for planet in self.planets:
            planet.update()

        # Now update all the Squads in the Universe
        for squad in self.squads:
            squad.update()

        # Time Slow
        time.sleep(self.time_slow)
        self.time_slow *= .9

        # Do we only have one team left?
        # FIXME
        """
        team_counts = Counter([s.team for s in self.all_ships])
        if len(team_counts.keys()) == 1 and not self.wave_over:
            self.wave_over = True
            if 'earth' in team_counts:
                self.comms.announce('won_match')
            else:
                self.comms.announce('lost_match')
        """

    def draw(self):
        """Let all the entities in the Universe draw themselves"""

        # Ships first
        for ship in self.all_ships:
            ship.draw()

        # Planets next
        for planet in self.planets:
            planet.draw()

        # Draw Text
        if self.current_text:
            self.game_engine.draw_text(self.current_text)

        # Countdown timer
        if self.initial_count_down:
            time.sleep(5)
            self.initial_count_down = False

    def collision_detection(self):
        """Detect if any entity is colliding with another entity"""

        # Test for collisions between all entities in the Universe
        # Note: This has lots of room for improvement (spacial hierarchies/etc)

        # First: Torps vs Zerg Ships
        zerg_ships = self.battle_info.zerg_ships()
        for torp in self.torps:
            for ship in zerg_ships:
                if force_utils.distance_between(torp, ship) < ship.p.shield_radius:
                    torp.impact(ship)

        # Second: Ships vs Ships
        for index, ship in enumerate(self.all_ships):
            for co_ship in self.all_ships[index+1:]:

                # Compute any collision forces
                (dx, dy), (co_dx, co_dy) = force_utils.repulsion_forces(ship, co_ship)
                ship.force_x += dx * co_ship.mass/ship.mass
                ship.force_y += dy * co_ship.mass/ship.mass
                co_ship.force_x += co_dx * ship.mass/co_ship.mass
                co_ship.force_y += co_dy * ship.mass/co_ship.mass

        # Third: Ships vs Planet
        for ship in self.all_ships:
            for planet in self.planets:

                # Compute any collision forces
                (dx, dy), (p_dx, p_dy) = force_utils.repulsion_forces(ship, planet)
                ship.force_x += dx * 10
                ship.force_y += dy * 10

        # Last: Ships against boundaries
        # Note: This is a 'hard' boundary
        for _ship in self.all_ships:
            ship_pad = self.pad/4
            _ship.x = min(max(_ship.x, ship_pad), self.width-ship_pad)
            _ship.y = min(max(_ship.y, ship_pad), self.height-ship_pad)

    def _space_out_planets(self):
        """Make sure planets don't overlap"""

        # First resolve any coincident planets
        force_utils.resolve_coincident(self.planets)

        # Now Space out the planets
        for _ in range(50):
            for _planet in self.planets:
                for co_planet in self.planets:
                    # Skip self
                    if _planet == co_planet:
                        continue
                    # Move if too close
                    if force_utils.distance_between(_planet, co_planet) < 350:
                        (dx, dy), (co_dx, co_dy) = force_utils.normalized_distance_vectors(_planet, co_planet)
                        _planet.x -= dx * 5
                        _planet.y -= dy * 5
                        co_planet.x -= co_dx * 5
                        co_planet.y -= co_dy * 5
                    # Boundaries
                    _planet.x = max(min(_planet.x, self.width-self.pad), self.pad)
                    _planet.y = max(min(_planet.y, self.height-self.pad), self.pad)


# Simple test of the Universe functionality
def test():
    from space_bots import game_engine_adapter
    from space_bots.squad import Squad
    from space_bots.ships import ship, miner, healer, tank, fighter, drone, zergling
    from space_bots.planet import Planet

    """Test for Universe Class"""

    # Create our Universe
    my_universe = Universe(1600, 1000, announcements=True)

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create two Pirate Squads (who doesn't want to be a pirate?)
    xpos = 300
    ypos = 850
    for squad_name in ['berserker', 'spitter', 'mega_bug']:
        my_squad = Squad(team='zerg', squad_name=squad_name, target_strategy='nearest')
        for _ in range(2):
            my_squad.add_ship(ship.Ship(my_game_engine, xpos, ypos, ship_type=squad_name, level=2))
        my_universe.add_squad(my_squad)
        xpos = 300
        ypos = 300

    # Add two zerg squads
    xpos = 300
    ypos = 150
    for squad_name in ['zerg1', 'zerg2']:
        zerg_squad = Squad(team='zerg', squad_name=squad_name, target_strategy='nearest')
        for _ in range(15):
            zerg_squad.add_ship(zergling.Zergling(my_game_engine, xpos, ypos))
        my_universe.add_squad(zerg_squad)
        xpos = 100
        ypos = 900

    # Create our Squad
    level = 1
    earth_squad = Squad(team='earth', squad_name='roughnecks', target_strategy='threat')
    my_miner = miner.Miner(my_game_engine, 850, 700, level=2)
    earth_squad.add_ship(my_miner)
    earth_squad.add_ship(healer.Healer(my_game_engine, 850, 700, level=2))
    earth_squad.add_ship(healer.Healer(my_game_engine, 850, 700, level=2))
    earth_squad.add_ship(tank.Tank(my_game_engine, 850, 700, level=2))
    for _ in range(2):
        earth_squad.add_ship(fighter.Fighter(my_game_engine, 850, 700, level=level))
    my_universe.add_squad(earth_squad)

    drone_squad = Squad(team='earth', squad_name='drones', target_strategy='nearest')
    for _ in range(2):
        drone_squad.add_ship(drone.Drone(my_game_engine, 850, 700, level=level))
    my_universe.add_squad(drone_squad)

    # Add some planets
    for _ in range(8):
        my_planet = Planet(my_game_engine, x=randint(800, 850), y=randint(500, 550))
        my_universe.add_planet(my_planet)

    # Explicitly call finalize on the Universe
    my_universe.finalize()

    # Position
    class Pos:
        pass
    Pos.x = 1200
    Pos.y = 500

    # Add Protection Orders
    earth_squad.protect(my_universe.battle_info.closest_planet(Pos))
    drone_squad.protect(my_miner, 30)

    # Have the Zerg squad target the miner
    zerg_squad.attack_target(my_miner)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
