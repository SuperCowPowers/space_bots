"""Weapon: Abstract Base Class for all weapons (lasers, tarp launchers, etc.)"""
from abc import ABC, abstractmethod


class Weapon(ABC):
    """Weapon: Abstract Base Class for all weapons (lasers, tarp launchers, etc.)"""
    def __init__(self, ship):
        self.my_ship = ship
        self.game_engine = self.my_ship.game_engine
        self.color = self.my_ship.p.color  # Do we want this?

    @abstractmethod
    def communicate(self, comms):
        """Weapons can post sounds and even announcements"""
        pass

    @abstractmethod
    def update(self, target=None):
        """Weapons update themselves, for instance Torp Launchers need to update Torps"""
        pass

    @abstractmethod
    def draw(self, target=None):
        """Draw the Weapon"""
        pass

    @abstractmethod
    def fire(self, target=None):
        """Fire the Weapon at the given target
           Note: Some Weapons (e.g. Lasers) will draw themselves when they are fired
        """
        pass


class NoWeapon(Weapon):
    """NoWeapon: Place a NoWeapon into a Ship Weapon Slot for Placeholder"""
    def __init__(self, ship):
        # Call SuperClass (Weapon) Initialization
        super().__init__(ship)

    def communicate(self, comms):
        """Weapons can post sounds and even announcements"""
        pass

    def update(self, target=None):
        """Weapons update themselves, for instance Torp Launchers need to update Torps"""
        pass

    def draw(self, target=None):
        """Draw the Weapon"""
        pass

    def fire(self, target=None):
        """Fire the Weapon at the given target
           Note: Some Weapons (e.g. Lasers) will draw themselves when they are fired
        """
        pass


# Simple test of the Weapon functionality
def test():
    """Test for Weapon Class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe
    from space_bots.ships.ship import Ship
    from space_bots.ships.fighter import Fighter

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Ship (has a Laser weapon and 'no weapon' for Torp Launcher
    my_ship = Ship(my_game_engine, 300, 500)
    my_universe.add_ship(my_ship, team='earth')

    # Create a Fighter (has a Laser weapon and a Torp Launcher)
    my_ship = Fighter(my_game_engine, 300, 500)
    my_universe.add_ship(my_ship, team='earth')

    # Create a Zerg Ship
    zerg = Ship(my_game_engine, 700, 500, ship_type='mega_bug')
    my_universe.add_ship(zerg, team='zerg')
    # Hack the zerg ship (no targeting)
    zerg.general_targeting = lambda: None
    zerg.force_x = -5000
    zerg.force_y = -5000

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
