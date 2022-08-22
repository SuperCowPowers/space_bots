"""Universe: Class that contains all the stuff"""
from random import randint


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

    def finalize(self):
        """Tasks to do after initial universe setup"""
        print('Universe Finalize...')
        # Space Planets Apart from each other
        self._space_out_planets()

        # We need a list of individual ships for collision detections
        squad_ships = [ship for _squad in self.squads for ship in _squad.ships]
        self.all_ships = self.individual_ships + squad_ships

        # Make sure Ship don't overlap each other
        self._space_out_ships()

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

    def draw(self):
        """Let all the entities in the Universe draw themselves"""
        for entity in self.all_entities:
            entity.draw()

    def collision_detection(self):
        """Detect if any entity is colliding with another entity"""

        # First ships against planets
        for _ship in self.all_ships:
            for _planet in self.planets:
                if _ship.collides(_planet):
                    delta = _ship.pos_delta(_planet, 0.1)
                    _ship.force_x -= delta[0]
                    _ship.force_y -= delta[1]

        # Second ships against ships
        for _ship in self.all_ships:
            for co_ship in self.all_ships:
                if _ship == co_ship:
                    continue
                if _ship.collides(co_ship):
                    delta = _ship.pos_delta(co_ship, 0.05)
                    _ship.force_x -= delta[0]
                    _ship.force_y -= delta[1]

        # Last ships against boundaries
        for _ship in self.all_ships:
            _ship.x = min(max(_ship.x, self.pad), self.width-self.pad)
            _ship.y = min(max(_ship.y, self.pad), self.height-self.pad)

    def closest_planet(self, ship):
        planet_distance = [(p, ship.distance_to(p)) for p in self.planets]
        planet_distance.sort(key=lambda tup: tup[1])
        return [p[0] for p in planet_distance][0]

    def _space_out_planets(self):
        """Make sure planets don't overlap"""
        for _ in range(50):
            for _planet in self.planets:
                for co_planet in self.planets:
                    # Skip self
                    if _planet == co_planet:
                        continue
                    # Move if too close
                    if _planet.distance_to(co_planet) < 350:
                        delta = _planet.pos_delta(co_planet)
                        _planet.x -= delta[0] / 10.0
                        _planet.y -= delta[1] / 10.0
                    # Boundaries
                    _planet.x = max(min(_planet.x, self.width-self.pad), self.pad)
                    _planet.y = max(min(_planet.y, self.height-self.pad), self.pad)

    def _space_out_ships(self):
        """Make sure ship don't overlap"""
        for _ in range(50):
            for _ship in self.all_ships:
                for co_ship in self.all_ships:
                    # Skip self
                    if _ship == co_ship:
                        continue
                    # Move if too close
                    if _ship.distance_to(co_ship) < 20:
                        _ship.x += randint(-5, 5)
                        _ship.y += randint(-5, 5)
                        delta = _ship.pos_delta(co_ship)
                        _ship.x -= delta[0]
                        _ship.y -= delta[1]
                    # Boundaries
                    _ship.x = max(min(_ship.x, self.width-self.pad), self.pad)
                    _ship.y = max(min(_ship.y, self.height-self.pad), self.pad)


# Simple test of the Universe functionality
def test():
    from space_bots import game_engine_adapter
    from space_bots.squad import Squad
    from space_bots.ship import Ship
    from space_bots.planet import Planet

    """Test for Universe Class"""

    # Create our Universe
    my_universe = Universe(1600, 1000)

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create our Squad
    my_squad = Squad(team='player', target_strategy='threat', stance='defensive')
    miner = Ship(my_game_engine, 900, 600, ship_type='miner')
    my_squad.add_ship(miner)
    healer = Ship(my_game_engine, 650, 600, ship_type='healer')
    my_squad.add_ship(healer)
    healer = Ship(my_game_engine, 650, 600, ship_type='healer')
    my_squad.add_ship(healer)
    shielder = Ship(my_game_engine, 700, 500, ship_type='shielder')
    my_squad.add_ship(shielder)
    shielder = Ship(my_game_engine, 700, 500, ship_type='shielder')
    my_squad.add_ship(shielder)
    fighter = Ship(my_game_engine, 850, 500, ship_type='fighter')
    my_squad.add_ship(fighter)

    # Create a Pirate Squad (who doesn't want to be a pirate?)
    pirate_squad = Squad(team='pirate', target_strategy='nearest', stance='offensive')
    miner = Ship(my_game_engine, 100, 100, ship_type='miner')
    pirate_squad.add_ship(miner)
    healer = Ship(my_game_engine, 150, 100, ship_type='healer')
    pirate_squad.add_ship(healer)
    healer = Ship(my_game_engine, 150, 100, ship_type='healer')
    pirate_squad.add_ship(healer)
    shielder = Ship(my_game_engine, 200, 100, ship_type='shielder')
    pirate_squad.add_ship(shielder)
    shielder = Ship(my_game_engine, 200, 100, ship_type='shielder')
    pirate_squad.add_ship(shielder)
    fighter = Ship(my_game_engine, 250, 100, ship_type='fighter')
    pirate_squad.add_ship(fighter)

    # Give our Squads the Battle State (universal in this case)
    my_squad.give_battle_state(my_universe)
    pirate_squad.give_battle_state(my_universe)

    # Add both Squads to the Universe
    my_universe.add_squad(my_squad)
    my_universe.add_squad(pirate_squad)

    # Add some planets
    for _ in range(8):
        my_planet = Planet(my_game_engine, x=randint(500, 550), y=randint(500, 550))
        my_universe.add_planet(my_planet)

    # Add Protection Orders
    my_squad.protect(my_universe.closest_planet(my_squad.ships[0]))

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
