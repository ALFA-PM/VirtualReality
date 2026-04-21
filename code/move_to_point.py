import cosysairsim as airsim
import time

vehicle = "Drone1"
client = airsim.MultirotorClient(ip="127.0.0.1")
client.confirmConnection()

client.enableApiControl(True, vehicle)
client.armDisarm(True, vehicle)

def pos():
    p = client.getMultirotorState(vehicle_name=vehicle).kinematics_estimated.position
    return (p.x_val, p.y_val, p.z_val)

print("Start:", pos())

# Make sure drone is in stable flight
client.hoverAsync(vehicle_name=vehicle).join()
time.sleep(1)

# Read current x,y only
p = client.getMultirotorState(vehicle_name=vehicle).kinematics_estimated.position

target_x = p.x_val + 20
target_y = p.y_val
target_z = -20   # IMPORTANT: use fixed flight altitude

print("Moving to:", target_x, target_y, target_z)

client.moveToPositionAsync(
    target_x, target_y, target_z, 5,
    vehicle_name=vehicle
).join()

client.hoverAsync(vehicle_name=vehicle).join()
time.sleep(1)

print("End:", pos())
print("DONE")