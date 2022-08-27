"""ShipCatalog: Class for the Getting Ship Specs"""

ship_buffs = {
    'protection':
        {'effects': {'incoming_damage_modifier': -0.1},
         'timer': 0,
         'display': False
         },
    'kings':
        {'effects': {'threat_modifier': -0.5},
         'timer': 0,
         'display': False
         },
    'take_the_pain':
        {'effects': {'extra_shield': 800},
         'timer': 10,  # If the shield isn't used up expire after 10 seconds
         'display': False,  # The extra_shield will show but no additional buff effect
         },
    'fortitude':
        {'effects': {'hp_modifier': 0.2},
         'timer': 0,
         'display': False
         },
    'salvation':
        {'effects': {'heal': 500},
         'timer': 5,
         'display': False
         },
    'ape_shit':
        {'effects': {'outgoing_damage_modifier': 0.5},
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
