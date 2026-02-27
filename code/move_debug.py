import cosysairsim as airsim
import time

vehicle = "Drone1"
client = airsim.MultirotorClient()
client.confirmConnection()

client.enableApiControl(True, vehicle)
client.armDisarm(True, vehicle)

def get_pos():
    p = client.getMultirotorState(vehicle_name=vehicle).kinematics_estimated.position
    return (p.x_val, p.y_val, p.z_val)

print("Before:", get_pos())

# IMPORTANT: hold altitude exactly (use current Z, don't guess)
x0, y0, z0 = get_pos()
x1, y1, z1 = x0 + 20, y0, z0  # move forward 20m, keep same Z

print("Commanding moveToPosition:", (x1, y1, z1))
client.moveToPositionAsync(x1, y1, z1, 5, vehicle_name=vehicle).join()

time.sleep(0.5)
print("After:", get_pos())
print("DONE")