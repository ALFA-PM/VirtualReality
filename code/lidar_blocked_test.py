import cosysairsim as airsim
import math
import time

LIDAR_NAME = "LidarFront"
VEHICLE = "Drone1"

def blocked_ahead(client, dist_thresh=8.0):
    data = client.getLidarData(lidar_name=LIDAR_NAME, vehicle_name=VEHICLE)
    pts = data.point_cloud

    # point_cloud = [x1,y1,z1, x2,y2,z2, ...] in sensor frame (meters)
    count_close_front = 0

    for i in range(0, len(pts), 3):
        x = pts[i]
        y = pts[i+1]
        z = pts[i+2]
        d = math.sqrt(x*x + y*y + z*z)

        # "in front" cone: x forward, y narrow
        if x > 1.0 and abs(y) < 2.0 and d < dist_thresh:
            count_close_front += 1
            if count_close_front > 30:
                return True, count_close_front

    return False, count_close_front


client = airsim.MultirotorClient()
client.confirmConnection()

client.enableApiControl(True, VEHICLE)
client.armDisarm(True, VEHICLE)
client.hoverAsync(vehicle_name=VEHICLE).join()

print("Checking obstacle ahead for 10 seconds...")

for t in range(10):
    is_blocked, n = blocked_ahead(client, dist_thresh=8.0)
    print(f"{t}s  blocked={is_blocked}  close_points={n}")
    time.sleep(1)

print("DONE")