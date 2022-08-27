"""ShipCatalog: Class for the Getting Ship Specs"""

ship_specs = {
    'tank':
        {'color': (100, 100, 220),
         'mass': 60,
         'speed': 0.2,
         'radius': 20,
         'hp': 300,
         'shield': 500,
         'laser_range': 100,
         'laser_damage': 0.05,
         'laser_width': 5,
         'capacitor': 50,
         'ship_width': 6,
         'shield_width': 2,
         'shield_recharge': 0.05,
         'hull_recharge': 0.05,
         'keep_range': 0,
         'threat': 200
         },
    'healer':
        {'color': (100, 200, 100),
         'mass': 30,
         'speed': 0.25,
         'radius': 14,
         'hp': 150,
         'shield': 100,
         'laser_range': 140,
         'laser_damage': 0.2,
         'laser_width': 4,
         'capacitor': 20,
         'ship_width': 5,
         'shield_width': 2,
         'shield_recharge': 0.0025,
         'hull_recharge': 0.0025,
         'keep_range': 300,
         'threat': 100
         },
    'fighter':
        {'color': (180, 60, 200),
         'mass': 40,
         'speed': 0.2,
         'radius': 16,
         'hp': 200,
         'shield': 150,
         'laser_range': 160,
         'laser_damage': 0.25,
         'laser_width': 4,
         'capacitor': 30,
         'ship_width': 5,
         'shield_width': 2,
         'shield_recharge': 0.005,
         'hull_recharge': 0.005,
         'keep_range': 80,
         'threat': 50
         },
    'miner':
        {'color': (180, 160, 60),
         'mass': 40,
         'speed': 0.25,
         'radius': 12,
         'hp': 200,
         'shield': 150,
         'laser_range': 100,
         'laser_damage': 0.15,
         'laser_width': 8,
         'capacitor': 30,
         'ship_width': 5,
         'shield_width': 2,
         'shield_recharge': 0.005,
         'hull_recharge': 0.005,
         'keep_range': 400,
         'threat': 30
         },
    'drone':
        {'color': (180, 200, 100),
         'mass': 20,
         'speed': 0.6,
         'radius': 7,
         'hp': 60,
         'shield': 40,
         'laser_range': 50,
         'laser_damage': 0.05,
         'laser_width': 2,
         'capacitor': 10,
         'ship_width': 3,
         'shield_width': 1,
         'shield_recharge': 0.05,
         'hull_recharge': 0.05,
         'keep_range': 40,
         'threat': 20
         },
    'starbase':
        {'color': (100, 100, 200),
         'mass': 200,
         'speed': 0.05,
         'radius': 20,
         'hp': 800,
         'shield': 500,
         'laser_range': 250,
         'laser_damage': 0.7,
         'laser_width': 7,
         'capacitor': 100,
         'ship_width': 7,
         'shield_width': 3,
         'shield_recharge': 0.05,
         'hull_recharge': 0.05,
         'keep_range': 200,
         'threat': 400
         },
    'zergling':
        {'color': (200, 150, 100),
         'mass': 2,
         'speed': 0.8,
         'radius': 6,
         'hp': 50,
         'shield': 30,
         'laser_range': 50,
         'laser_damage': 0.05,
         'laser_width': 2,
         'capacitor': 10,
         'ship_width': 2,
         'shield_width': 1,
         'shield_recharge': 0.001,
         'hull_recharge': 0.001,
         'keep_range': 20,
         'threat': 20
         },
    'spitter':
        {'color': (200, 120, 100),
         'mass': 30,
         'speed': 0.25,
         'radius': 14,
         'hp': 150,
         'shield': 100,
         'laser_range': 140,
         'laser_damage': 0.15,
         'laser_width': 4,
         'capacitor': 20,
         'ship_width': 5,
         'shield_width': 2,
         'shield_recharge': 0.0025,
         'hull_recharge': 0.0025,
         'keep_range': 100,
         'threat': 80
         },
    'berserker':
        {'color': (180, 80, 80),
         'mass': 40,
         'speed': 0.2,
         'radius': 16,
         'hp': 200,
         'shield': 150,
         'laser_range': 120,
         'laser_damage': 0.25,
         'laser_width': 4,
         'capacitor': 30,
         'ship_width': 5,
         'shield_width': 2,
         'shield_recharge': 0.005,
         'hull_recharge': 0.005,
         'keep_range': 0,
         'threat': 50
         },
    'mega_bug':
        {'color': (160, 60, 80),
         'mass': 25,  # FIXME
         'speed': 1.0,
         'radius': 20,
         'hp': 800,
         'shield': 500,
         'laser_range': 120,
         'laser_damage': 0.35,
         'laser_width': 5,
         'capacitor': 100,
         'ship_width': 7,
         'shield_width': 2,
         'shield_recharge': 0.005,
         'hull_recharge': 0.005,
         'keep_range': 0,
         'threat': 400
         }
}
