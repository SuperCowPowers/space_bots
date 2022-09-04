"""ShipCatalog: Class for the Getting Ship Specs"""

ship_specs = {
    'tank':
        {'color': (100, 100, 220),
         'mass': 600,
         'speed': 0.3,
         'radius': 20,
         'hp': 300,
         'shield': 500,
         'laser_range': 100,
         'laser_damage': 0.1,
         'laser_width': 5,
         'capacitor': 100,
         'ship_width': 6,
         'shield_width': 2,
         'shield_recharge': 0.05,
         'hull_recharge': 0.05,
         'cap_recharge': 0.025,
         'keep_range': 0,
         'threat': 200,
         'max_torps': 8
         },
    'healer':
        {'color': (100, 200, 100),
         'mass': 300,
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
         'cap_recharge': 0.05,
         'keep_range': 300,
         'threat': 100
         },
    'fighter':
        {'color': (180, 60, 200),
         'mass': 400,
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
         'cap_recharge': 0.05,
         'keep_range': 140,
         'threat': 50
         },
    'miner':
        {'color': (180, 160, 60),
         'mass': 500,
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
         'cap_recharge': 0.05,
         'keep_range': 400,
         'threat': 30
         },
    'drone':
        {'color': (180, 200, 100),
         'mass': 150,
         'speed': 0.6,
         'radius': 7,
         'hp': 60,
         'shield': 40,
         'laser_range': 80,
         'laser_damage': 0.25,
         'laser_width': 2,
         'laser_heat': 1.5,
         'capacitor': 10,
         'ship_width': 3,
         'shield_width': 1,
         'shield_recharge': 0.1,  # Drones can't be healed, so nanobot repairs
         'hull_recharge': 0.1,
         'cap_recharge': 0.05,
         'keep_range': 60,
         'threat': 20
         },
    'starbase':
        {'color': (100, 100, 200),
         'mass': 2000,
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
         'cap_recharge': 0.05,
         'keep_range': 200,
         'threat': 400,
         'max_torps': 20
         },
    'zergling':
        {'color': (180, 130, 80),
         'mass': 20,
         'speed': 0.7,
         'radius': 6,
         'hp': 50,
         'shield': 30,
         'laser_range': 60,
         'laser_damage': 0.03,
         'laser_width': 2,
         'laser_heat': 1.1,
         'capacitor': 10,
         'ship_width': 2,
         'shield_width': 1,
         'shield_recharge': 0.001,
         'hull_recharge': 0.001,
         'cap_recharge': 0.05,
         'keep_range': 20,
         'threat': 20
         },
    'spitter':
        {'color': (180, 100, 80),
         'mass': 300,
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
         'cap_recharge': 0.05,
         'keep_range': 100,
         'threat': 80
         },
    'berserker':
        {'color': (160, 60, 60),
         'mass': 400,
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
         'cap_recharge': 0.05,
         'keep_range': 100,
         'threat': 50
         },
    'mega_bug':
        {'color': (140, 60, 80),
         'mass': 800,
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
         'cap_recharge': 0.05,
         'keep_range': 100,
         'threat': 400
         }
}
