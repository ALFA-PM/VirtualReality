import cosysairsim as airsim

client = airsim.MultirotorClient()
client.confirmConnection()

data = client.getLidarData(lidar_name="LidarFront", vehicle_name="Drone1")

print("Number of lidar points:", len(data.point_cloud))