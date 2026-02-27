import cosysairsim as airsim
import time
import math

VEHICLE_NAME = "Drone1"

# Mission order (Actor_2 is inside forbidden zone)
WAYPOINT_ACTOR_NAMES = ["Actor_1", "Actor_3", "Actor_5", "Actor_7", "Actor_9", "Actor_11", "Actor_2"]

SPEED_MPS = 8.0
WAIT_AT_WP_SEC = 5.0
ROOF_CLEARANCE_M = 14.0
EXTRA_CLEARANCE_M = 5.0
SAFE_Z_MARGIN_M = 0.0

# ===== ForbiddenZone TriggerBox values from Unreal (CENTIMETERS) =====
FORBIDDEN_CENTER_CM = (-14100.0, -9400.0, -50300.0)   # Location in cm
FORBIDDEN_EXTENT_CM = (5246.25, 4743.75, 3433.75)     # Box Extent (half-size) in cm
FORBIDDEN_YAW_DEG = -50.0                              # Rotation Z (Yaw) in degrees
SAFETY_MARGIN_M = 3.0                                  # expand by 3 meters (in XY)
# ===================================================================


def must_pose(client, name: str):
    pose = client.simGetObjectPose(name)
    if pose is None:
        raise RuntimeError(f"Could not find object '{name}'")
    return pose


def hover_wait(client, seconds: float):
    end_t = time.time() + seconds
    while time.time() < end_t:
        client.hoverAsync(vehicle_name=VEHICLE_NAME).join()
        time.sleep(0.5)


def forbidden_params_m():
    """Convert forbidden box from cm to m and return (cx, cy, ex, ey, yaw_rad)."""
    cx = FORBIDDEN_CENTER_CM[0] / 100.0
    cy = FORBIDDEN_CENTER_CM[1] / 100.0
    ex = FORBIDDEN_EXTENT_CM[0] / 100.0 + SAFETY_MARGIN_M
    ey = FORBIDDEN_EXTENT_CM[1] / 100.0 + SAFETY_MARGIN_M
    yaw = math.radians(FORBIDDEN_YAW_DEG)
    return cx, cy, ex, ey, yaw


def point_in_forbidden_xy(x_m, y_m) -> bool:
    """
    Check if a point (x,y) in METERS is inside the ROTATED forbidden TriggerBox in XY.
    """
    cx, cy, ex, ey, yaw = forbidden_params_m()

    # translate to box center
    dx = x_m - cx
    dy = y_m - cy

    # rotate by -yaw to align world point into box-local axes
    c = math.cos(-yaw)
    s = math.sin(-yaw)
    lx = dx * c - dy * s
    ly = dx * s + dy * c

    return (abs(lx) <= ex) and (abs(ly) <= ey)


def segment_intersects_aabb(x0, y0, x1, y1, xmin, xmax, ymin, ymax) -> bool:
    """
    Liang–Barsky line clipping for axis-aligned rectangle.
    Returns True if the segment intersects the rectangle.
    """
    dx = x1 - x0
    dy = y1 - y0

    p = [-dx, dx, -dy, dy]
    q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]

    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)

    return u1 <= u2


def segment_crosses_forbidden_xy(x0_m, y0_m, x1_m, y1_m) -> bool:
    """
    Check if the straight path in XY from start->end intersects the ROTATED forbidden box.
    Do this by transforming both endpoints into box-local coordinates, then AABB intersect.
    """
    cx, cy, ex, ey, yaw = forbidden_params_m()
    c = math.cos(-yaw)
    s = math.sin(-yaw)

    def to_local(x, y):
        dx = x - cx
        dy = y - cy
        lx = dx * c - dy * s
        ly = dx * s + dy * c
        return lx, ly

    lx0, ly0 = to_local(x0_m, y0_m)
    lx1, ly1 = to_local(x1_m, y1_m)

    return segment_intersects_aabb(lx0, ly0, lx1, ly1, -ex, ex, -ey, ey)


def main():
    client = airsim.MultirotorClient()
    client.confirmConnection()

    print("Connected!")
    print("Client Ver:", client.getClientVersion(), "Server Ver:", client.getServerVersion())

    client.enableApiControl(True, vehicle_name=VEHICLE_NAME)
    client.armDisarm(True, vehicle_name=VEHICLE_NAME)

    print("\nTaking off...")
    client.takeoffAsync(vehicle_name=VEHICLE_NAME).join()
    time.sleep(1.0)

    # Read waypoint positions and roof heights
    waypoints = []
    roof_zs = []
    print("\nReading waypoint roof positions:")
    for idx, name in enumerate(WAYPOINT_ACTOR_NAMES, start=1):
        pose = must_pose(client, name)

        x = pose.position.x_val
        y = pose.position.y_val
        z_roof = pose.position.z_val
        z_target = z_roof - ROOF_CLEARANCE_M  # NED: smaller z = higher

        waypoints.append((idx, name, x, y, z_roof, z_target))
        roof_zs.append(z_roof)

        print(f"WP {idx} ({name}): x={x:.3f}, y={y:.3f}, roof_z={z_roof:.3f}, target_z={z_target:.3f}")

    # SAFE_Z (as in your code)
    min_roof_z = min(roof_zs)
    SAFE_Z = min_roof_z - (ROOF_CLEARANCE_M + EXTRA_CLEARANCE_M + SAFE_Z_MARGIN_M)
    print(f"\nSAFE_Z computed: {SAFE_Z:.3f} (NED; more negative = higher)")

    print("\nClimbing to SAFE_Z first...")
    client.moveToZAsync(SAFE_Z, SPEED_MPS, vehicle_name=VEHICLE_NAME).join()
    time.sleep(0.5)

    last_safe = None  # (x,y,z,name)

    for idx, name, x, y, z_roof, z_target in waypoints:
        z_cmd = min(z_target, SAFE_Z)

        # current drone position (meters)
        state = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
        pos = state.kinematics_estimated.position
        x0, y0 = pos.x_val, pos.y_val

        # ====== HARD BLOCK RULES (what you requested) ======
        # 1) If TARGET is in forbidden zone -> log and stay at last safe (Actor_11)
        if point_in_forbidden_xy(x, y):
            client.simPrintLogMessage("ForbiddenZone", f"TARGET FORBIDDEN: {name}", severity=2)
            print(f"\nForbiddenZone: TARGET FORBIDDEN -> {name}")

            # stay where we are / last safe
            client.hoverAsync(vehicle_name=VEHICLE_NAME).join()
            print("Staying at last safe waypoint (no move).")
            break

        # 2) If straight PATH crosses forbidden zone -> log and stay (do not move)
        if segment_crosses_forbidden_xy(x0, y0, x, y):
            client.simPrintLogMessage("ForbiddenZone", f"PATH FORBIDDEN to: {name}", severity=2)
            print(f"\nForbiddenZone: PATH CROSSES FORBIDDEN -> {name}")

            client.hoverAsync(vehicle_name=VEHICLE_NAME).join()
            print("Staying at last safe waypoint (no move).")
            break
        # ====================================================

        print(f"\nFlying to WP {idx} ({name}) at z_cmd={z_cmd:.3f}")

        client.moveToPositionAsync(
            x, y, z_cmd,
            SPEED_MPS,
            timeout_sec=120,
            vehicle_name=VEHICLE_NAME
        ).join()

        client.hoverAsync(vehicle_name=VEHICLE_NAME).join()

        last_safe = (x, y, z_cmd, name)
        client.simPrintLogMessage(f"Building {idx}:", " COLOR DELIVERED", severity=0)
        hover_wait(client, WAIT_AT_WP_SEC)

    print("\nMission complete.")
    client.simPrintLogMessage("Mission:", "DONE", severity=2)
    client.hoverAsync(vehicle_name=VEHICLE_NAME).join()


if __name__ == "__main__":
    main()