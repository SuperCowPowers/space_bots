"""Universe: Class that contains all the stuff"""
import time
from random import randint

# Local Imports
from space_bots import force_utils


class Universe:
    """Universe: Class that contains all the stuff"""
    # Note: Maybe refactor/rethink how this class should be used later
    #      - Collision Detection should be a separate class

    def __init__(self, width=1600, height=1000):
        """Initialize the Universe class"""
        self.game_engine = None
        self.pad = 150
        self.width = width
        self.height = height
        self.planets = []
        self.squads = []
        self.all_ships = []
        self.individual_ships = []
        self.all_entities = []
        self.individual_entities = []
        self.is_finalized = False
        self.time_slow = 0.05
        self.initial_count_down = False

    def finalize(self):
        """Tasks to do after initial universe setup"""
        print('Universe Finalize...')
        # Space Planets Apart from each other
        self._space_out_planets()

        # We need a list of individual ships for collision detections
        squad_ships = [ship for _squad in self.squads for ship in _squad.ships]
        self.all_ships = self.individual_ships + squad_ships

        # All entities are collected into one big list
        self.all_entities = self.planets + self.squads + self.individual_ships + self.individual_entities

        # All done
        self.is_finalized = True

    def set_game_engine(self, game_engine):
        print('Universe: set_game_engine...')
        self.game_engine = game_engine

    def add_entity(self, entity):
        """Add a Planet to the Universe"""
        self.individual_entities.append(entity)

    def add_planet(self, planet):
        """Add a Planet to the Universe"""
        self.planets.append(planet)

    def add_squad(self, squad):
        """Add a Squad to the Universe"""
        self.squads.append(squad)

    def add_ship(self, ship):
        """Add a Ship to the Universe"""
        self.individual_ships.append(ship)

    def remove_ship(self, ship):
        """Remove a Ship from the Universe"""
        self.individual_ships.remove(ship)
        self.all_ships.remove(ship)

    def communicate(self):
        """Let all the entities in the Universe communicate"""

        # No one is going to remember to call finalize
        if not self.is_finalized:
            self.finalize()

        # Have all the entities communicate
        for entity in self.all_entities:
            entity.communicate()

    def update(self):
        """Let all the entities in the Universe update themselves"""

        # First lets remove any dead ships
        self.all_ships = [s for s in self.all_ships if not s.is_dead()]

        # Now run collision detection
        self.collision_detection()

        # Now update all the entities in the Universe
        for entity in self.all_entities:
            entity.update()

        # Time Slow
        if any([s.in_combat for s in self.squads]):
            time.sleep(self.time_slow)
            self.time_slow *= .99

    def draw(self):
        """Let all the entities in the Universe draw themselves"""

        # Ships first
        for ship in self.all_ships:
            ship.draw()

        # Planets next
        for planet in self.planets:
            planet.draw()

        # Countdown timer
        if self.initial_count_down:
            time.sleep(5)
            self.initial_count_down = False

    def collision_detection(self):
        """Detect if any entity is colliding with another entity"""

        # Test for collisions between all entities in the Universe
        # Note: This has lots of room for improvement (spacial hierarchies/etc)

        # First: Ships vs Ships
        for index, ship in enumerate(self.all_ships):
            for co_ship in self.all_ships[index+1:]:

                # Compute any collision forces
                (dx, dy), (co_dx, co_dy) = force_utils.repulsion_forces(ship, co_ship)
                ship.force_x += dx * 2
                ship.force_y += dy * 2
                co_ship.force_x += co_dx * 2
                co_ship.force_y += co_dy * 2

        # Next: Ships vs Planet
        for ship in self.all_ships:
            for planet in self.planets:

                # Compute any collision forces
                (dx, dy), (p_dx, p_dy) = force_utils.repulsion_forces(ship, planet)
                ship.force_x += dx * 10
                ship.force_y += dy * 10

        # Last: Ships against boundaries
        # FIXME
        # Note: We're not setting force here as this is a 'hard' boundary
        for _ship in self.all_ships:
            _ship.x = min(max(_ship.x, self.pad/4), self.width-self.pad/4)
            _ship.y = min(max(_ship.y, self.pad/4), self.height-self.pad/4)

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
    from space_bots import game_engine_adapter, battle_state
    from space_bots.squad import Squad
    from space_bots.ships.ship import Ship
    from space_bots.ships import miner, healer, tank
    from space_bots.planet import Planet

    """Test for Universe Class"""

    # Create our Universe
    my_universe = Universe(1600, 1000)

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create our Squad
    my_squad = Squad(team='good guys', squad_name='roughnecks', target_strategy='threat', stance='defensive')
    miner = miner.Miner(my_game_engine, 1000, 600)
    my_squad.add_ship(miner)
    healer = healer.Healer(my_game_engine, 950, 600)
    my_squad.add_ship(healer)
    tank = tank.Tank(my_game_engine, 950, 600)
    my_squad.add_ship(tank)
    fighter = Ship(my_game_engine, 950, 500, ship_type='fighter')
    my_squad.add_ship(fighter)
    fighter = Ship(my_game_engine, 980, 680, ship_type='fighter')
    my_squad.add_ship(fighter)
    fighter = Ship(my_game_engine, 900, 600, ship_type='fighter')
    my_squad.add_ship(fighter)

    # Create a Pirate Squad (who doesn't want to be a pirate?)
    pirate_squad = Squad(team='pirate', squad_name='xenos', target_strategy='nearest', stance='offensive')
    healer = Ship(my_game_engine, 200, 200, ship_type='shaman')
    pirate_squad.add_ship(healer)
    healer = Ship(my_game_engine, 200, 200, ship_type='shaman')
    pirate_squad.add_ship(healer)
    healer = Ship(my_game_engine, 200, 200, ship_type='shaman')
    pirate_squad.add_ship(healer)
    healer = Ship(my_game_engine, 200, 200, ship_type='shaman')
    pirate_squad.add_ship(healer)
    fighter = Ship(my_game_engine, 200, 200, ship_type='berserker')
    pirate_squad.add_ship(fighter)
    fighter = Ship(my_game_engine, 200, 200, ship_type='berserker')
    pirate_squad.add_ship(fighter)
    fighter = Ship(my_game_engine, 250, 200, ship_type='berserker')
    pirate_squad.add_ship(fighter)
    fighter = Ship(my_game_engine, 250, 200, ship_type='berserker')
    pirate_squad.add_ship(fighter)

    # Add a zerg
    zerg_squad = Squad(team='pirate', squad_name='zerg', target_strategy='low_health', stance='offensive')
    for _ in range(30):
        zerg_squad.add_ship(Ship(my_game_engine, x=randint(200, 320), y=randint(800, 900), ship_type='scout'))

    # Give our Squads the Battle State (universal in this case)
    my_battle_state = battle_state.BattleState(my_universe)
    my_squad.set_battle_state(my_battle_state)
    pirate_squad.set_battle_state(my_battle_state)
    zerg_squad.set_battle_state(my_battle_state)

    # Add both Squads to the Universe
    my_universe.add_squad(zerg_squad)
    my_universe.add_squad(pirate_squad)
    my_universe.add_squad(my_squad)

    # Add some planets
    for _ in range(8):
        my_planet = Planet(my_game_engine, x=randint(800, 850), y=randint(500, 550))
        my_universe.add_planet(my_planet)

    # Add Protection Orders
    my_squad.protect(my_battle_state.closest_planet(my_squad.ships[0]))

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
