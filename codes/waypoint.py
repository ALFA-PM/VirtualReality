import cosysairsim as airsim
import time

VEHICLE_NAME = "Drone1"

# Order: Actor_1 -> Actor_11
WAYPOINT_ACTOR_NAMES = ["Actor_1", "Actor_3", "Actor_5", "Actor_7", "Actor_9", "Actor_11"]

SPEED_MPS = 8.0
HOVER_SEC = 1.0

ROOF_CLEARANCE_M = 14.0   # meters ABOVE each roof marker


def must_pose(client, name: str):
    pose = client.simGetObjectPose(name)
    if pose is None:
        raise RuntimeError(f"Could not find object '{name}'")
    return pose


def main():
    client = airsim.MultirotorClient()
    client.confirmConnection()

    print("Connected!")
    print("Client Ver:", client.getClientVersion(),
          "Server Ver:", client.getServerVersion())

    client.enableApiControl(True, vehicle_name=VEHICLE_NAME)
    client.armDisarm(True, vehicle_name=VEHICLE_NAME)

    # Takeoff
    print("\nTaking off...")
    client.takeoffAsync(vehicle_name=VEHICLE_NAME).join()
    time.sleep(1.0)

    # Read waypoint positions
    waypoints = []

    print("\nReading waypoint roof positions:")
    for name in WAYPOINT_ACTOR_NAMES:
        pose = must_pose(client, name)

        x = pose.position.x_val
        y = pose.position.y_val
        z_roof = pose.position.z_val

        # fly above roof
        z_target = z_roof - ROOF_CLEARANCE_M

        waypoints.append((name, x, y, z_target))

        print(f"{name}: x={x:.3f}, y={y:.3f}, roof_z={z_roof:.3f}, target_z={z_target:.3f}")

    # Move to first waypoint altitude smoothly
    print("\nAdjusting altitude to first waypoint height...")
    client.moveToZAsync(
        waypoints[0][3],
        SPEED_MPS,
        vehicle_name=VEHICLE_NAME
    ).join()

    time.sleep(0.5)

    # Fly through waypoints
    for i, (name, x, y, z_target) in enumerate(waypoints, start=1):

        print(f"\nFlying to {name} ({i}/{len(waypoints)})")

        client.moveToPositionAsync(
            x,
            y,
            z_target,
            SPEED_MPS,
            timeout_sec=120,
            vehicle_name=VEHICLE_NAME
        ).join()

        client.hoverAsync(vehicle_name=VEHICLE_NAME).join()

        # SHOW EXACT WHITE MESSAGE ON SCREEN
        client.simPrintLogMessage(
            "Color DELIVERED",
            "",
            severity=0   # white color
        )

        time.sleep(HOVER_SEC)

    print("\nMission complete.")
    client.simPrintLogMessage(
        "Mission",
        "DONE",
        severity=2
    )

    client.hoverAsync(vehicle_name=VEHICLE_NAME).join()


if __name__ == "__main__":
    main()