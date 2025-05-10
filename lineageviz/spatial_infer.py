# spatial_infer.py
import numpy as np

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def infer_daughter_positions(parent_pos, division_angle_deg, prev_vector=None, 
                             volume_left=0.5, volume_right=0.5, shape='sphere'):
    """
    Infers 3D positions for daughter cells given:
    - parent_pos: tuple (x, y, z)
    - division_angle_deg: angle from previous division vector in degrees
    - prev_vector: previous division orientation (unit vector)
    - volume_left/right: sizes of daughters
    - shape: 'sphere' or 'ellipsoid'
    Returns: tuple of left_pos, right_pos
    """
    parent_pos = np.array(parent_pos)
    angle_rad = np.radians(division_angle_deg)

    # If no previous vector is provided, default to z-axis
    if prev_vector is None:
        prev_vector = np.array([0, 0, 1])
    else:
        prev_vector = normalize(np.array(prev_vector))

    # Create an arbitrary orthogonal vector
    if np.allclose(prev_vector, [0, 0, 1]):
        ortho = np.array([1, 0, 0])
    else:
        ortho = normalize(np.cross(prev_vector, [0, 0, 1]))

    # Rotate ortho around prev_vector by angle_rad to get division vector
    axis = prev_vector
    cos_theta = np.cos(angle_rad)
    sin_theta = np.sin(angle_rad)
    ux, uy, uz = axis
    R = np.array([
        [cos_theta + ux**2 * (1 - cos_theta),      ux*uy*(1 - cos_theta) - uz*sin_theta, ux*uz*(1 - cos_theta) + uy*sin_theta],
        [uy*ux*(1 - cos_theta) + uz*sin_theta, cos_theta + uy**2 * (1 - cos_theta),      uy*uz*(1 - cos_theta) - ux*sin_theta],
        [uz*ux*(1 - cos_theta) - uy*sin_theta, uz*uy*(1 - cos_theta) + ux*sin_theta, cos_theta + uz**2 * (1 - cos_theta)]
    ])
    div_vector = normalize(R @ ortho)

    # Distance between daughters based on radii
    rL = (3 * volume_left / (4 * np.pi)) ** (1/3)
    rR = (3 * volume_right / (4 * np.pi)) ** (1/3)
    separation = rL + rR + 0.2  # add small buffer

    offset_vector = div_vector * (separation / 2)
    left_pos = parent_pos - offset_vector
    right_pos = parent_pos + offset_vector

    return tuple(left_pos), tuple(right_pos)

# Optional: helper to recursively assign positions to a tree
def position_tree(tree, root_name='P0', parent_pos=(0,0,0), prev_vector=None):
    positions = {root_name: parent_pos}
    queue = [(root_name, parent_pos, prev_vector)]

    while queue:
        parent, ppos, prev = queue.pop(0)
        node = tree.get(parent, {})
        daughters = node.get("daughters", [])
        if len(daughters) == 2:
            l, r = daughters
            angle = node.get("division_angle", 90)
            volL = node.get("left_volume", 0.5)
            volR = node.get("right_volume", 0.5)
            lp, rp = infer_daughter_positions(ppos, angle, prev, volL, volR)
            positions[l] = lp
            positions[r] = rp
            queue.append((l, lp, np.array(rp) - np.array(lp)))
            queue.append((r, rp, np.array(lp) - np.array(rp)))

    return positions
