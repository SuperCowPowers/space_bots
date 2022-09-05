"""Mounts: Mounts for Laser Guns for Space Bots"""
import math

# Local Imports
from space_bots.utils import force_utils


class CenterMount:
    def __init__(self, ship):
        self.my_ship = ship
        self.mount_points = [(self.my_ship.x, self.my_ship.y)]

    def update(self, target):
        self.mount_points = [(self.my_ship.x, self.my_ship.y)]

    def draw(self):
        pass

    def num_mount_points(self):
        return len(self.mount_points)

    def get_mount_locations(self):
        return self.mount_points


class GimbalMount:
    def __init__(self, ship):
        self.my_ship = ship
        self.game_engine = ship.game_engine
        self.color = ship.p.color
        self.radius = self.my_ship.p.shield_radius - 1
        self.offset_theta = math.pi / 2
        self.target_theta = self.offset_theta
        self.mount_points = self._compute_mount_rotation()

    def _compute_mount_rotation(self):
        """Internal: Compute the mount points based on the angle to the target
           FIXME: Simplify/Optimize this logic
        """
        first_mount = (self.radius * math.cos(self.target_theta), self.radius * math.sin(self.target_theta))
        second_mount = (-first_mount[0], -first_mount[1])
        first_mount = (first_mount[0] + self.my_ship.x, first_mount[1] + self.my_ship.y)
        second_mount = (second_mount[0] + self.my_ship.x, second_mount[1] + self.my_ship.y)
        return [first_mount, second_mount]

    def update(self, target):
        if target:
            self.target_theta = force_utils.get_angle(self.my_ship, target) + self.offset_theta
        else:
            self.target_theta = 0
        self.mount_points = self._compute_mount_rotation()



    def draw(self):
        """Draw the Gimbal Mounts"""
        for mount in self.mount_points:
            self.game_engine.draw_circle(self.color, mount, 6, width=0)
            self.game_engine.draw_circle((220, 220, 220), mount, 7, width=1)

    def num_mount_points(self):
        return len(self.mount_points)

    def get_mount_locations(self):
        return self.mount_points
