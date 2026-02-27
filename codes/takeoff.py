import cosysairsim as airsim
import time

# connect to drone
client = airsim.MultirotorClient()
client.confirmConnection()

print("Enabling API control...")
client.enableApiControl(True)

print("Arming drone...")
client.armDisarm(True)

# stabilize hover
print("Stabilizing...")
client.hoverAsync().join()

time.sleep(2)

# optional: move higher to safer altitude
print("Moving to altitude -20 meters...")
client.moveToZAsync(-20, 3).join()

print("Drone ready for mission.")