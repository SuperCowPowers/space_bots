"""Healer: A Healer ship in Space Bots"""

# Local Imports
from space_bots.utils import weapon, force_utils
from space_bots.ships import ship


class Healer(ship.Ship):
    """Healer: A Healer ship in Space Bots"""
    def __init__(self, game_engine, x=300, y=300, level=1):

        # Call SuperClass (Entity) Initialization
        super().__init__(game_engine, x, y, ship_type='healer', level=level)

        # Healer specific stuff
        self.healing_target = None
        self.salvation_thrown = False
        self.blood_pact_thrown = False
        self.squad_buffs = ['fortitude']
        self.laser_guns = weapon.NoWeapon(self)  # Healer don't have lasers

        # Healing Level adjustments
        pass

    def update(self):
        """Update the Healer"""

        # General updates
        self.general_ship_updates()
        self.general_avoidance(passive=2.0)  # Healer needs to avoid enemies

        # Get the lowest health TeamMate and move towards them
        self.healing_target = self.battle_info.lowest_health_teammate(self)
        if self.healing_target and self.healing_target != self:
            (_, _), (dx, dy) = force_utils.attraction_forces(self.healing_target, self, self.p.laser_range/1.2)
            self.force_x += dx
            self.force_y += dy

            # Cast Salvation
            if self.healing_target.health_percent() < .05 and not self.salvation_thrown:
                self.announcer_messages.put('healer_cast_salvation')
                self.healing_target.add_buff('salvation')
                self.salvation_thrown = True

            # Cast Blood Pact
            if self.healing_target.health_percent() < .12 and not self.blood_pact_thrown:
                self.announcer_messages.put('healer_cast_blood_pact')
                avg_health_percent = self.squad.average_health() - 0.10  # Blood tax :)
                for _ship in self.squad.ships:
                    if _ship != self.healing_target:
                        _ship.add_buff('blood_pact', avg_health_percent=avg_health_percent)
                    else:
                        _ship.add_buff('blood_pact_target')

                self.blood_pact_thrown = True

        # Now actually call the move command
        self.move()

    def draw(self):
        """Draw the entire ship"""
        self.draw_healing_laser()
        super().draw()

    def draw_healing_laser(self):
        """Draw the mining lasers"""
        if self.healing_target and force_utils.distance_between(self, self.healing_target) < self.p.laser_range:

            # Does my target need healing
            if self.healing_target.health_percent() < .99:
                self.game_engine.draw_line(self.p.color, (self.x, self.y), (self.healing_target.x, self.healing_target.y),
                                           width=self.p.laser_width + self.level)
                self.healing_target.heal(self.p.laser_damage)


# Simple test of the Healer functionality
def test():
    """Test for Healer Class"""
    from space_bots import game_engine_adapter, asteroid
    from space_bots.universe import Universe
    from space_bots.ships.miner import Miner

    # Create a Universe
    my_universe = Universe()

    # Create the Game Engine
    my_game_engine = game_engine_adapter.GameEngineAdapter(my_universe)

    # Give the universe the game engine
    my_universe.set_game_engine(my_game_engine)

    # Create a Asteroid
    my_asteroid = asteroid.Asteroid(my_game_engine, 500, 500)
    my_universe.add_asteroid(my_asteroid)

    # Create a Healer ship and a Miner Ship
    healer_ship = Healer(my_game_engine, 300, 300)
    my_universe.add_ship(healer_ship, team='earth')
    miner_ship = Miner(my_game_engine, 400, 400)
    my_universe.add_ship(miner_ship, team='earth')

    # Give the miner some damage to heal up
    miner_ship.damage(300)

    # Invoke the event loop
    my_game_engine.event_loop()


if __name__ == "__main__":
    test()
