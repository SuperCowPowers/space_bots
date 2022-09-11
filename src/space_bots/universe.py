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

        # Dimensions and Boundaries
        self.pad = 50
        self.width = width
        self.height = height
        self.top = self.pad
        self.bottom = self.height - 3 * self.pad
        self.left = self.pad
        self.right = self.width - self.pad

        # Track asteroids, squads, ships, and torpedoes
        self.asteroids = []
        self.squads = []
        self.all_ships = []
        self.torps = []

        # Universe State vars
        self.is_finalized = False
        self.initial_count_down = False
        self.wave_over = False
        self.top_text = None
        self.bottom_text = None
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
        self._space_out_asteroids()
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

    def add_asteroid(self, asteroid):
        """Add a Asteroid to the Universe"""
        self.asteroids.append(asteroid)

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
            self.bottom_text = display_text

        # Log messages sent to the universe
        for message in self.comms.get_messages('universe'):
            print(f"Comms: {message}")

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

        # Build a torpedo list from the ships
        self.torps = []
        for ship in self.all_ships:
            self.torps += ship.get_torps()

        # Now run collision detection
        self.collision_detection()

        # Update/Manage the buffs for all the ships
        self.buffs.update()

        # Now update all the Asteroids in the Universe
        for asteroid in self.asteroids:
            asteroid.update()

        # Now update all the Squads in the Universe
        for squad in self.squads:
            squad.update()

        # Time Slow
        # time.sleep(self.time_slow)
        # self.time_slow *= .9

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

        # Asteroids next
        for asteroid in self.asteroids:
            asteroid.draw()

        # Draw Text
        if self.top_text:
            self.game_engine.draw_text(self.top_text, pos='top')
        if self.bottom_text:
            self.game_engine.draw_text(self.bottom_text)

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
                if force_utils.distance_between(torp, ship) < ship.p.collision_radius:
                    torp.impact(ship)

        # Second: Ships vs Ships
        for index, ship in enumerate(self.all_ships):
            for co_ship in self.all_ships[index+1:]:

                # Compute any collision forces
                ship_spacing = ship.pad_radius + co_ship.pad_radius
                (dx, dy), (co_dx, co_dy) = force_utils.repulsion_forces(ship, co_ship, ship_spacing)
                ship.force_x += dx * co_ship.mass/ship.mass
                ship.force_y += dy * co_ship.mass/ship.mass
                co_ship.force_x += co_dx * ship.mass/co_ship.mass
                co_ship.force_y += co_dy * ship.mass/co_ship.mass

        # Third: Ships vs Asteroid
        for ship in self.all_ships:
            for asteroid in self.asteroids:
                # Compute any collision forces
                (dx, dy), (p_dx, p_dy) = force_utils.repulsion_forces(ship, asteroid)
                ship.force_x += dx * 10  # Asteroids are big
                ship.force_y += dy * 10

        # Fourth: Asteroid vs Asteroid
        for index, asteroid in enumerate(self.asteroids):
            for co_asteroid in self.asteroids[index+1:]:
                (dx, dy), (co_dx, co_dy) = force_utils.repulsion_forces(asteroid, co_asteroid)
                asteroid.force_x += dx * 10
                asteroid.force_y += dy * 10
                co_asteroid.force_x += co_dx * 10
                co_asteroid.force_y += co_dy * 10

        # Fifth: Ships against boundaries (bounce effect)
        for _ship in self.all_ships:
            if _ship.x < self.left or _ship.x > self.right:
                _ship.force_x = -_ship.force_x
            if _ship.y < self.top or _ship.y > self.bottom:
                _ship.force_y = -_ship.force_y

        # Last: Asteroids against boundaries (bounce effect)
        for asteroid in self.asteroids:
            if asteroid.x < self.left or asteroid.x > self.right:
                asteroid.force_x = -asteroid.force_x
            if asteroid.y < self.top or asteroid.y > self.bottom:
                asteroid.force_y = -asteroid.force_y

    def _space_out_asteroids(self):
        """Make sure asteroids don't overlap"""

        # First resolve any coincident asteroids
        force_utils.resolve_coincident(self.asteroids)

        # Now Space out the asteroids
        for _ in range(50):
            for _asteroid in self.asteroids:
                for co_asteroid in self.asteroids:
                    # Skip self
                    if _asteroid == co_asteroid:
                        continue
                    # Move if too close
                    if force_utils.distance_between(_asteroid, co_asteroid) < 400:
                        (dx, dy), (co_dx, co_dy) = force_utils.normalized_distance_vectors(_asteroid, co_asteroid)
                        _asteroid.x -= dx * 5
                        _asteroid.y -= dy * 5
                        co_asteroid.x -= co_dx * 5
                        co_asteroid.y -= co_dy * 5
                    # Boundaries
                    _asteroid.x = max(min(_asteroid.x, self.right), self.left)
                    _asteroid.y = max(min(_asteroid.y, self.bottom), self.top)


# Simple test of the Universe functionality
def test():
    from space_bots import game_engine_adapter
    from space_bots.asteroid import Asteroid

    """Test for Universe Class"""

    # Create our Universe
    my_universe = Universe(1600, 1000, announcements=True)

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Get the Universe Mission Planner
    my_mission = my_universe.mission_planner
    my_mission.set_mission(18, test_squads=True)

    # Add some asteroids
    for _ in range(5):
        my_asteroid = Asteroid(my_game_engine, x=randint(500, 1000), y=randint(500, 600))
        my_universe.add_asteroid(my_asteroid)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
