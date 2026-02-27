import cosysairsim as airsim
import time

client = airsim.MultirotorClient()
client.confirmConnection()

client.enableApiControl(True)
client.armDisarm(True)

print("Stabilizing...")
client.hoverAsync().join()

print("Moving forward 10 meters...")
client.moveByVelocityAsync(3, 0, 0, 5).join()

print("Hover")
client.hoverAsync().join()

print("DONE")