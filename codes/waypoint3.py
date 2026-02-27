import cosysairsim as airsim
import time
import math

VEHICLE_NAME = "Drone1"

WAYPOINT_ACTOR_NAMES = ["Actor_1", "Actor_3", "Actor_5", "Actor_7", "Actor_9", "Actor_11", "Actor_2", "Actor_4"]

SPEED_MPS = 8.0
WAIT_AT_WP_SEC = 5.0
ROOF_CLEARANCE_M = 14.0
EXTRA_CLEARANCE_M = 5.0

# ✅ FIX: fly higher than forbidden box so path-cross test doesn't trigger at Actor_1
SAFE_Z_MARGIN_M = 30.0

FORBIDDEN_CENTER_CM = (-14100.0, -9400.0, 50300.0)    # (FIXED Z SIGN)
FORBIDDEN_EXTENT_CM = (5246.25, 4743.75, 3433.75)
FORBIDDEN_YAW_DEG = -50.0
SAFETY_MARGIN_M = 3.0


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
    cx = FORBIDDEN_CENTER_CM[0] / 100.0
    cy = FORBIDDEN_CENTER_CM[1] / 100.0
    cz = FORBIDDEN_CENTER_CM[2] / 100.0
    ex = FORBIDDEN_EXTENT_CM[0] / 100.0 + SAFETY_MARGIN_M
    ey = FORBIDDEN_EXTENT_CM[1] / 100.0 + SAFETY_MARGIN_M
    ez = FORBIDDEN_EXTENT_CM[2] / 100.0
    yaw = math.radians(FORBIDDEN_YAW_DEG)
    return cx, cy, cz, ex, ey, ez, yaw


def point_in_forbidden_xyz(x_m, y_m, z_m) -> bool:
    cx, cy, cz, ex, ey, ez, yaw = forbidden_params_m()

    dx = x_m - cx
    dy = y_m - cy

    c = math.cos(-yaw)
    s = math.sin(-yaw)
    lx = dx * c - dy * s
    ly = dx * s + dy * c

    in_xy = (abs(lx) <= ex) and (abs(ly) <= ey)
    in_z = (abs(z_m - cz) <= ez)
    return in_xy and in_z


def segment_intersects_aabb(x0, y0, x1, y1, xmin, xmax, ymin, ymax) -> bool:
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
    cx, cy, cz, ex, ey, ez, yaw = forbidden_params_m()

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

    waypoints = []
    roof_zs = []
    print("\nReading waypoint roof positions:")
    for idx, name in enumerate(WAYPOINT_ACTOR_NAMES, start=1):
        pose = must_pose(client, name)

        x = pose.position.x_val
        y = pose.position.y_val
        z_roof = pose.position.z_val
        z_target = z_roof - ROOF_CLEARANCE_M

        waypoints.append((idx, name, x, y, z_roof, z_target))
        roof_zs.append(z_roof)

        print(f"WP {idx} ({name}): x={x:.3f}, y={y:.3f}, roof_z={z_roof:.3f}, target_z={z_target:.3f}")

    min_roof_z = min(roof_zs)
    SAFE_Z = min_roof_z - (ROOF_CLEARANCE_M + EXTRA_CLEARANCE_M + SAFE_Z_MARGIN_M)
    print(f"\nSAFE_Z computed: {SAFE_Z:.3f} (NED; more negative = higher)")

    print("\nClimbing to SAFE_Z first...")
    client.moveToZAsync(SAFE_Z, SPEED_MPS, vehicle_name=VEHICLE_NAME).join()
    time.sleep(0.5)

    for idx, name, x, y, z_roof, z_target in waypoints:
        z_cmd = min(z_target, SAFE_Z)

        state = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
        pos = state.kinematics_estimated.position
        x0, y0, z0 = pos.x_val, pos.y_val, pos.z_val

        if point_in_forbidden_xyz(x, y, z_cmd):
            client.simPrintLogMessage("ForbiddenZone", f"TARGET FORBIDDEN: {name}", severity=2)
            print(f"\nForbiddenZone: TARGET FORBIDDEN -> {name}")

            # Hold at SAFE_Z so you can see the forbidden zone
            try:
                client.moveToZAsync(SAFE_Z, SPEED_MPS, vehicle_name=VEHICLE_NAME).join()
            except Exception as e:
                print(f"[WARN] moveToZAsync failed: {e}")

            print("Holding at SAFE_Z (no move).")
            client.simPrintLogMessage("Mission:", "HOLDING AT SAFE_Z (FORBIDDEN)", severity=1)
            hover_wait(client, 15.0)
            break

        cx, cy, cz, ex, ey, ez, yaw = forbidden_params_m()
        in_forbidden_z = (abs(z0 - cz) <= ez) or (abs(z_cmd - cz) <= ez)

        if in_forbidden_z and segment_crosses_forbidden_xy(x0, y0, x, y):
            client.simPrintLogMessage("ForbiddenZone", f"PATH FORBIDDEN to: {name}", severity=2)
            print(f"\nForbiddenZone: PATH CROSSES FORBIDDEN -> {name}")

            # Hold at SAFE_Z so you can see the forbidden zone
            try:
                client.moveToZAsync(SAFE_Z, SPEED_MPS, vehicle_name=VEHICLE_NAME).join()
            except Exception as e:
                print(f"[WARN] moveToZAsync failed: {e}")

            print("Holding at SAFE_Z (no move).")
            client.simPrintLogMessage("Mission:", "HOLDING AT SAFE_Z (FORBIDDEN)", severity=1)
            hover_wait(client, 15.0)
            break

        print(f"\nFlying to WP {idx} ({name}) at z_cmd={z_cmd:.3f}")

        client.moveToPositionAsync(
            x, y, z_cmd,
            SPEED_MPS,
            timeout_sec=120,
            vehicle_name=VEHICLE_NAME
        ).join()

        client.hoverAsync(vehicle_name=VEHICLE_NAME).join()

        if name == "Actor_2":
            # small painting movement
            BOUNCE_M = 0.5
            z_down = max(z_cmd + BOUNCE_M, z_target)
            z_up = z_cmd - BOUNCE_M

            client.simPrintLogMessage("Drone is PAINTING:", "COMPLETED", severity=0)

            try:
                client.moveToZAsync(z_down, 2.0, vehicle_name=VEHICLE_NAME).join()
                time.sleep(0.05)
                client.moveToZAsync(z_up, 6.0, vehicle_name=VEHICLE_NAME).join()
                time.sleep(0.05)
                client.moveToZAsync(z_cmd, 3.0, vehicle_name=VEHICLE_NAME).join()
                client.hoverAsync(vehicle_name=VEHICLE_NAME).join()
            except Exception as e:
                print(f"[WARN] Actor_2 painting move failed: {e}")

            # ===== After Actor_2 painting: check NEXT actor (Actor_4) WITHOUT moving, then stop =====
            try:
                next_name = "Actor_4"
                next_pose = must_pose(client, next_name)

                nx = next_pose.position.x_val
                ny = next_pose.position.y_val
                nz_roof = next_pose.position.z_val
                nz_target = nz_roof - ROOF_CLEARANCE_M
                nz_cmd = min(nz_target, SAFE_Z)

                # Current drone position
                state2 = client.getMultirotorState(vehicle_name=VEHICLE_NAME)
                pos2 = state2.kinematics_estimated.position
                cx0, cy0, cz0 = pos2.x_val, pos2.y_val, pos2.z_val

                forbidden = False

                if point_in_forbidden_xyz(nx, ny, nz_cmd):
                    forbidden = True
                    client.simPrintLogMessage("ForbiddenZone", f"TARGET FORBIDDEN: {next_name}", severity=2)
                    print(f"\nForbiddenZone: TARGET FORBIDDEN -> {next_name}")
                else:
                    bx, by, bcz, bex, bey, bez, byaw = forbidden_params_m()
                    in_forbidden_z2 = (abs(cz0 - bcz) <= bez) or (abs(nz_cmd - bcz) <= bez)

                    if in_forbidden_z2 and segment_crosses_forbidden_xy(cx0, cy0, nx, ny):
                        forbidden = True
                        client.simPrintLogMessage("ForbiddenZone", f"PATH FORBIDDEN to: {next_name}", severity=2)
                        print(f"\nForbiddenZone: PATH CROSSES FORBIDDEN -> {next_name}")

                # Hold at SAFE_Z so you can see forbidden zone
                client.moveToZAsync(SAFE_Z, SPEED_MPS, vehicle_name=VEHICLE_NAME).join()
                client.hoverAsync(vehicle_name=VEHICLE_NAME).join()

                if forbidden:
                    print("Holding at SAFE_Z (forbidden ahead).")
                    client.simPrintLogMessage("Mission:", "HOLDING AT SAFE_Z (FORBIDDEN AHEAD)", severity=1)
                else:
                    print("ForbiddenZone: stop")
                    client.simPrintLogMessage("ForbiddenZone", "STOPPED (PREVIEW)", severity=2)

                hover_wait(client, 15.0)
            except Exception as e:
                print(f"[WARN] Post-Actor_2 forbidden preview failed: {e}")

            break
            # ==========================================================================================
            # ==========================================================================================


    print("\nMission complete.")
    client.simPrintLogMessage("Mission:", "DONE", severity=2)
    client.hoverAsync(vehicle_name=VEHICLE_NAME).join()


if __name__ == "__main__":
    main()