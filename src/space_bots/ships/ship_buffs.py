"""ShipCatalog: Class for the Getting Ship Specs"""

ship_buffs = {
    'protection':
        {'effects': {'incoming_damage_modifier': 0.9},
         'display': False
         },
    'kings':
        {'effects': {'threat_modifier': -0.5},
         'display': False
         },
    'take_the_pain':
        {'effects': {'shield': 500},
         'display': False
         },
    'fortitude':
        {'effects': {'hp_modifier': 1.2},
         'display': False
         },
    'salvation':
        {'effects': {'heal': 700},
         'timer': 5,
         'display': False
         },
    'first_strike':
        {'effects': {'laser_range_modifier': 2.0},
         'timer': 5,
         'display': True,
         'color': (180, 60, 200)
         },
    'ape_shit':
        {'effects': {'outgoing_damage_modifier': 1.5},
         'timer': 2,
         'display': True,
         'color': (220, 100, 100)
         },
    'poison':
        {'effects': {'damage_over_time': 0.5},
         'timer': 10,
         'display': True,
         'color': (220, 100, 100)
         }
}
