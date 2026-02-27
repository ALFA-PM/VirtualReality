import cosysairsim as airsim

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True, "Drone1")
client.armDisarm(True, "Drone1")

print("Move the drone to the desired waypoint (manually).")
print("Then press ENTER here to record it. Type 'q' + Enter to quit.\n")

i = 1
while True:
    s = input(f"[{i}] Press Enter to record waypoint, or 'q' to quit: ").strip().lower()
    if s == "q":
        break

    p = client.getMultirotorState(vehicle_name="Drone1").kinematics_estimated.position
    print(f"WAYPOINT {i}:  x={p.x_val:.2f}, y={p.y_val:.2f}, z={p.z_val:.2f}\n")
    i += 1

print("Done.")