"""ShipParameters: Class for setting up a Ship Parameters (what it is)"""

# Local imports
from space_bots.ships.specs.ship_catalog import ship_specs


class ShipParameters:
    """ShipParameters: Class for setting up a Ship Parameters (what it is)"""
    def __init__(self, ship_type):
        """Set up all the various ship parameters"""
        self.ship_type = ship_type
        self.color = ship_specs[ship_type]['color']
        self.mass = ship_specs[ship_type]['mass']
        self.speed = ship_specs[ship_type]['speed']
        self.radius = ship_specs[ship_type]['radius']
        self.hp = ship_specs[ship_type]['hp']
        self.shield = ship_specs[ship_type]['shield']
        self.laser_range = ship_specs[ship_type]['laser_range']
        self.laser_damage = ship_specs[ship_type]['laser_damage']
        self.laser_width = ship_specs[ship_type]['laser_width']
        self.laser_heat = ship_specs[ship_type].get('laser_heat', 2)
        self.capacitor = ship_specs[ship_type]['capacitor']
        self.shield_recharge = ship_specs[ship_type]['shield_recharge']
        self.hull_recharge = ship_specs[ship_type]['hull_recharge']
        self.cap_recharge = ship_specs[ship_type]['cap_recharge']
        self.ship_width = ship_specs[ship_type]['ship_width']
        self.shield_width = ship_specs[ship_type]['shield_width']
        self.keep_range = ship_specs[ship_type]['keep_range']
        self.threat = ship_specs[ship_type]['threat']
        self.incoming_damage_modifier = ship_specs[ship_type].get('incoming_damage_modifier', 1.0)
        self.outgoing_damage_modifier = ship_specs[ship_type].get('outgoing_damage_modifier', 1.0)
        self.targeting_lock_avoidance = ship_specs[ship_type].get('targeting_lock_avoidance', 0.0)
        self.max_torps = ship_specs[ship_type].get('max_torps', 0)
        self.shield_radius = self.radius + self.shield_width
        self.collision_radius = self.shield_radius
