import cosysairsim as airsim
import time

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

target_z = -15  # keep this altitude

def pos():
    p = client.getMultirotorState().kinematics_estimated.position
    return (p.x_val, p.y_val, p.z_val)

print("Start:", pos())

client.hoverAsync().join()
time.sleep(1)

print("Move forward while holding Z...")
# Move to a position 15 meters ahead, with fixed Z
p0 = client.getMultirotorState().kinematics_estimated.position
x1 = p0.x_val + 15
y1 = p0.y_val
client.moveToPositionAsync(x1, y1, target_z, 5).join()

client.hoverAsync().join()
time.sleep(1)

print("End:", pos())
print("DONE")