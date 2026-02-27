import cosysairsim as airsim
import time

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

def pos():
    p = client.getMultirotorState().kinematics_estimated.position
    return (p.x_val, p.y_val, p.z_val)

print("Start position:", pos())

client.hoverAsync().join()
time.sleep(1)

print("Moving forward...")
client.moveByVelocityAsync(3, 0, 0, 5).join()
client.hoverAsync().join()
time.sleep(1)

print("End position:", pos())
print("DONE")