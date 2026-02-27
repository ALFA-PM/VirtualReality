import cosysairsim as airsim
import time

client = airsim.MultirotorClient()
client.confirmConnection()

print("Enable API control")
client.enableApiControl(True)

print("Arm")
client.armDisarm(True)

print("Hover stabilize")
client.hoverAsync().join()
time.sleep(1)

# Optional mission altitude (keep it if you want)
print("Go to Z = -20")
client.moveToZAsync(-20, 3).join()

print("READY")