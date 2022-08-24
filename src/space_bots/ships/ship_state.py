"""ShipState: Class for Managing all the Ship State"""

# Local imports
from space_bots.ships.ship_catalog import ship_specs
from space_bots.ships.ship_buffs import ship_buffs


class ShipState:
    """ShipState: Class for Managing all the Ship State"""
    def __init__(self, ship_type):
        """Set up the ship state"""
        self.hp = ship_specs[ship_type]['hp']
        self.shield = ship_specs[ship_type]['shield']
        self.extra_shield = 0
        self.capacitor = ship_specs[ship_type]['capacitor']
        self.buffs = set()
        self.buff_info = ship_buffs

        # Targeting
        self.target = None
