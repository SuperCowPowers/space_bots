"""ShipState: Class for Managing all the Ship State"""

# Local imports
from space_bots.ships.ship_catalog import ship_specs


class ShipState:
    """ShipState: Class for Managing all the Ship State"""
    def __init__(self, ship_type):
        """Set up the ship state"""
        self.hp = ship_specs[ship_type]['hp']
        self.shield = ship_specs[ship_type]['shield']
        self.capacitor = ship_specs[ship_type]['capacitor']

        # Targeting
        self.target = None
        self.non_targets = []
