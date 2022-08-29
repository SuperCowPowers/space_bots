"""Buff Manager tracks timed buffs, removing them when the timer is up"""
import time
from collections import defaultdict

# Local imports
from space_bots.ships import ship_buffs


class BuffManager:
    """"Buff Manager tracks timed buffs, removing them when the timer is up
       Usage:
            buffs = BuffManager()
            buffs.apply(buff_name, ship)  # Applies the buff to the ship
            buffs.update()  # Check buffs/timers and remove when expired
            buffs.clear()   # Clear all buffs from all ships
    """
    def __init__(self):
        """BuffManager Initialization"""
        self._buff_info = ship_buffs.ship_buffs
        self.ship_buffs = defaultdict(dict)

    def apply(self, buff_name, ship):
        """Apply a previous registered buff to the ship
           Args:
               buff_name: The name of the buff
               ship: The ship to apply the buff to
           Returns:
               boolean: True or False
        """
        # Record the expiration time
        if self._buff_info[buff_name].get('timer'):
            expire = time.time() + self._buff_info[buff_name]['timer']
        else:
            expire = None
        my_buff_info = self._buff_info[buff_name].copy()
        my_buff_info['expire'] = expire
        self.ship_buffs[ship][buff_name] = my_buff_info

        # Now actually apply the buff effect
        effects = my_buff_info['effects']

        # FIXME: This seems like a bad/suboptimal way to apply buffs
        for effect, value in effects.items():
            if effect == 'laser_range_modifier':
                ship.p.laser_range *= value
            elif effect == 'hp_modifier':
                ship.p.hp *= value
            elif effect == 'incoming_damage_modifier':
                ship.p.incoming_damage_modifier *= value
            elif effect == 'shield':
                ship.s.shield += value
            elif effect == 'heal':
                ship.s.hp += value
            else:
                print(f"{buff_name}: Don't know how to apply")
        print(effects)

    def buff_me(self, ship):
        """Make changes to the ship's state/parameters to reflect all the current buffs"""
        pass

    def get_visible_buffs(self, ship):
        """Return any visible buffs to the ship, so they can draw them"""
        visible_buffs = []
        for buff_name, buff_info in self.ship_buffs[ship].items():
            if buff_info['display']:
                visible_buffs.append(buff_info)
        return visible_buffs

    def update(self):
        """Check all the current buffs for expirations"""
        now = time.time()
        for ship, all_buffs in self.ship_buffs.items():
            for buff_name in list(all_buffs.keys()):
                if all_buffs[buff_name]['expire'] and all_buffs[buff_name]['expire'] < now:
                    del(all_buffs[buff_name])

    def clear(self):
        """Clear all the buffs"""
        for ship, buff_info in self.ship_buffs.items():
            for buff_name, timer in buff_info.items():
                ship.remove_buff(buff_name)
        self.ship_buffs = defaultdict(dict)

    def dump_buffs(self):
        """Dump the current set of buffs (for debugging)"""
        for ship, buff_info in self.ship_buffs.items():
            for buff_name, timer in buff_info.items():
                print(f"{ship.squad}:{ship}:{buff_name}:{timer}")

    def dump_buff_info(self):
        """Dump the current set of buffs (for debugging)"""
        for buff_name, buff_info in self._buff_info.items():
            print(f"{buff_name}")
            print(f"{buff_info}")


def test():
    """Test for the BuffManager class"""
    from space_bots import game_engine_adapter
    from space_bots.universe import Universe
    from space_bots.ships.fighter import Fighter

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create two ships (one more massive than another
    my_ship = Fighter(my_game_engine, 200, 200)
    my_universe.add_ship(my_ship, team='earth')

    # Add the Universe BuffManager
    # buffs = my_universe.buffs

    # Apply a buff to a ship
    # buffs.apply('ape_shit', my_ship)

    # Invoke the event loop and the buff should 'wear off' in 5/10 seconds...
    my_game_engine.event_loop()


if __name__ == '__main__':

    # Run the test
    test()
