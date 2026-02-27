import cosysairsim as airsim
import time

VEHICLE = "Drone1"
SPEED_XY = 2.0
SPEED_Z = 1.5

client = airsim.MultirotorClient(ip="127.0.0.1")
client.confirmConnection()
client.enableApiControl(True, VEHICLE)
client.armDisarm(True, VEHICLE)

def get_pos():
    p = client.getMultirotorState(vehicle_name=VEHICLE).kinematics_estimated.position
    return p.x_val, p.y_val, p.z_val

def print_pos(prefix="Position"):
    x, y, z = get_pos()
    print(f"{prefix}: x={x:.2f}, y={y:.2f}, z={z:.2f}")

def move_to(tx, ty, tz, speed):
    client.moveToPositionAsync(tx, ty, tz, speed, vehicle_name=VEHICLE).join()
    client.hoverAsync(vehicle_name=VEHICLE).join()
    time.sleep(1.0)

print("Connected.")
print("Simple commands:")
print("  f N     -> forward  N meters (x +)")
print("  b N     -> back     N meters (x -)")
print("  r N     -> right    N meters (y +)")
print("  l N     -> left     N meters (y -)")
print("  u N     -> up       N meters (try both u/d if your z sign is unusual)")
print("  d N     -> down     N meters")
print("  save    -> save current position")
print("  pos     -> show current position")
print("  q       -> quit")
print()

client.hoverAsync(vehicle_name=VEHICLE).join()
time.sleep(1.0)
print_pos("Start")

waypoints = []

while True:
    cmd = input("> ").strip().lower()

    if cmd == "q":
        break
    if cmd == "save":
        x, y, z = get_pos()
        wp = (round(x, 2), round(y, 2), round(z, 2))
        waypoints.append(wp)
        print(f"Saved WP{len(waypoints)}: {wp}")
        continue
    if cmd == "pos":
        print_pos("Current")
        continue

    parts = cmd.split()
    if len(parts) != 2:
        print("Invalid command. Example: f 5 | r 2 | u 3 | save")
        continue

    direction, value_str = parts
    try:
        dist = float(value_str)
    except ValueError:
        print("Distance must be a number.")
        continue

    x, y, z = get_pos()
    tx, ty, tz = x, y, z
    speed = SPEED_XY

    if direction == "f":
        tx = x + dist
    elif direction == "b":
        tx = x - dist
    elif direction == "r":
        ty = y + dist
    elif direction == "l":
        ty = y - dist
    elif direction == "u":
        # In many AirSim setups: up = z becomes more negative
        tz = z - dist
        speed = SPEED_Z
    elif direction == "d":
        tz = z + dist
        speed = SPEED_Z
    else:
        print("Unknown direction. Use f/b/r/l/u/d.")
        continue

    print(f"Moving to: x={tx:.2f}, y={ty:.2f}, z={tz:.2f}")
    move_to(tx, ty, tz, speed)
    print_pos("Now at")

print("\nRecorded waypoints:")
for i, wp in enumerate(waypoints, 1):
    print(f"WP{i} = {wp}")

print("\nWAYPOINTS = [")
for i, (x, y, z) in enumerate(waypoints, 1):
    print(f'    ({x}, {y}, {z}, "WP{i}", "inspect_roof"),')
print("]")

print("\nDONE")