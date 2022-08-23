"""ForceUtils: A set of Operations to compute forces on space_bot Entities"""
import math
from random import uniform


def distance_between(source, target):
    dx = target.x - source.x
    dy = target.y - source.y
    return math.sqrt(dx ** 2 + dy ** 2)


def normalized_distance_vectors(source, target):

    # Compute source to target vector
    st_dx = target.x - source.x
    st_dy = target.y - source.y
    mag = math.sqrt(st_dx**2 + st_dy**2)
    n_st = (st_dx/mag, st_dy/mag)

    # Target to Source is just the negative
    n_ts = (-n_st[0], -n_st[1])
    return n_st, n_ts


def repulsion_forces(source, target, rest_distance=None):
    """A TWO body repulsive force calculation"""

    # Default for rest distance is the combination of collision radi
    if rest_distance is None:
        rest_distance = (source.collision_radius + target.collision_radius)

    # If my current distance > rest_distance then 'rest'
    cur_distance = distance_between(source, target)
    if cur_distance > rest_distance:
        return (0, 0), (0, 0)

    # Are we coincident?
    if cur_distance < 0.001:
        # Force a position change (just source is fine)
        source.x += uniform(-10, 10)
        source.y += uniform(-10, 10)
        return (0, 0), (0, 0)

    # Okay the repulsion will be greater the closer we are
    # Note: We know with logic above that cur_distance != 0.0
    repulsion_factor = 1000.0/(cur_distance*cur_distance)

    # Compute normalized distance vectors
    norm_st, norm_ts = normalized_distance_vectors(source, target)

    # Final Repulsion Calculation
    source_repulsion = (-norm_st[0] * repulsion_factor, -norm_st[1] * repulsion_factor)
    target_repulsion = (-source_repulsion[0], -source_repulsion[1])  # Opposite
    return source_repulsion, target_repulsion


def attraction_forces(source, target, within_range):
    """A TWO body attractive force calculation"""

    # If my current distance < within_range then no force
    cur_distance = distance_between(source, target)
    if cur_distance < within_range:
        return (0, 0), (0, 0)

    # Okay the attraction will be greater the further away we are
    max_attraction_factor = 100000
    attraction_factor = min(cur_distance*cur_distance, max_attraction_factor) * 0.0001

    # Compute normalized distance vectors
    norm_st, norm_ts = normalized_distance_vectors(source, target)

    # Final Attraction Calculation
    source_attraction = (norm_st[0] * attraction_factor, norm_st[1] * attraction_factor)
    target_attraction = (-source_attraction[0], -source_attraction[1])  # Opposite
    return source_attraction, target_attraction


def force_based_movement(entity, limit=None):
    """Move the Entity based on it's current forces, mass, and limits (if any)"""
    delta_x = entity.force_x / (entity.mass*entity.mass)
    delta_y = entity.force_y / (entity.mass*entity.mass)
    if limit is not None:
        delta_x = max(min(delta_x, limit), -limit)
        delta_y = max(min(delta_y, limit), -limit)
    entity.x += delta_x
    entity.y += delta_y


def resolve_coincident(entity_list):
    """Make sure that all entities do not coincide"""

    for e1 in entity_list:
        for e2 in entity_list:
            cur_distance = distance_between(e1, e2)

            # Are we coincident?
            if cur_distance < 0.001:
                # Force a position change (just e1 is fine)
                e1.x += uniform(-10, 10)
                e1.y += uniform(-10, 10)


# Simple test of the ForceUtils functionality
def test():
    """Test for ForceUtils Functionality"""

    # Two test entities
    class FakeEntity:
        def __init__(self, x, y, cr, mass):
            self.x = x
            self.y = y
            self.collision_radius = cr
            self.mass = mass

    a = FakeEntity(5, 5, 3, 10)
    b = FakeEntity(10, 10, 3, 10)

    print(distance_between(a, b))
    print('<< Normalized Distance Vectors >>')
    print(normalized_distance_vectors(a, b))

    # Should be zero forces since they are outside the rest distance
    print(repulsion_forces(a, b))

    # Should be small forces since they are slightly inside the rest distance
    b = FakeEntity(9, 9, 3, 10)
    print('<< Small Repulsion >>')
    print(distance_between(a, b))
    print(repulsion_forces(a, b))

    # Should be larger forces since they are getting very close
    b = FakeEntity(5.5, 5.5, 3, 10)
    print('<< Large Repulsion >>')
    print(distance_between(a, b))
    print(repulsion_forces(a, b))

    # Should be zero since we specified a very small rest distance
    b = FakeEntity(5.5, 5.5, 3, 10)
    print(distance_between(a, b))
    print(repulsion_forces(a, b, rest_distance=0.1))

    # Test Coincident
    b = FakeEntity(5, 5, 3, 10)
    print(distance_between(a, b))
    print(repulsion_forces(a, b))

    # Mass Test: A More massive object should move less with equal force
    a = FakeEntity(5, 5, 3, 1)
    b = FakeEntity(6, 6, 3, 10)
    print(distance_between(a, b))
    (a.force_x, a.force_y), (b.force_x, b.force_y) = repulsion_forces(a, b)
    print(repulsion_forces(a, b))

    print('<< Repulsion Movement >>')
    a_x = a.x
    a_y = a.y
    b_x = b.x
    b_y = b.y
    force_based_movement(a)
    force_based_movement(b)
    print(f'A moved: {a.x-a_x}, {a.y-a_y}')
    print(f'B moved: {b.x-b_x}, {b.y-b_y}')

    # Attractive Forces
    a = FakeEntity(5, 5, 3, 10)
    b = FakeEntity(10, 10, 3, 10)

    # Should be zero forces since they are within the range
    print('<< Attractive Forces >>')
    print(distance_between(a, b))
    print(attraction_forces(a, b, 10))

    # Should be small forces since they are slightly outside the range
    b = FakeEntity(20, 20, 3, 10)
    print(attraction_forces(a, b, 10))

    # Should be medium forces since they are further out
    b = FakeEntity(50, 50, 3, 10)
    print(attraction_forces(a, b, 10))

    # Should be larger forces since they are far from range
    b = FakeEntity(500, 500, 3, 10)
    print(attraction_forces(a, b, 10))


if __name__ == "__main__":
    test()
