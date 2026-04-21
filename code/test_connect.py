import cosysairsim as airsim

print("Creating client...")
client = airsim.MultirotorClient(ip="127.0.0.1")

print("Trying confirmConnection...")
client.confirmConnection()

print("Connected to drone successfully")

# Check current drone position (relative to PlayerStart, in NED)
state = client.getMultirotorState(vehicle_name="Drone1")
p = state.kinematics_estimated.position

print("Drone1 position:")
print("X =", p.x_val)
print("Y =", p.y_val)
print("Z =", p.z_val)