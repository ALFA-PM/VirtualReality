import math
import cosysairsim as airsim

def quat_to_euler(q):
    # q: airsim.Quaternionr with (w_val, x_val, y_val, z_val)
    w, x, y, z = q.w_val, q.x_val, q.y_val, q.z_val

    # roll (x-axis rotation)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # pitch (y-axis rotation)
    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)

    # yaw (z-axis rotation)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


client = airsim.MultirotorClient(ip="127.0.0.1")
client.confirmConnection()

vehicle_name = "Drone1"
print("Connected!\n")

# 1) estimated state (NED)
state = client.getMultirotorState(vehicle_name=vehicle_name)
p_est = state.kinematics_estimated.position

print("=== Kinematics Estimated (NED, meters) ===")
print(f"X (North): {p_est.x_val}")
print(f"Y (East):  {p_est.y_val}")
print(f"Z (Down):  {p_est.z_val}")

# 2) ground truth (NED)
kin_gt = client.simGetGroundTruthKinematics(vehicle_name=vehicle_name)
p_gt = kin_gt.position

print("\n=== Ground Truth Kinematics (NED, meters) ===")
print(f"X (North): {p_gt.x_val}")
print(f"Y (East):  {p_gt.y_val}")
print(f"Z (Down):  {p_gt.z_val}")

# 3) pose (NED) + orientation
pose = client.simGetVehiclePose(vehicle_name=vehicle_name)
p_pose = pose.position

print("\n=== simGetVehiclePose Position (NED, meters) ===")
print(f"X (North): {p_pose.x_val}")
print(f"Y (East):  {p_pose.y_val}")
print(f"Z (Down):  {p_pose.z_val}")

roll, pitch, yaw = quat_to_euler(pose.orientation)

print("\n=== Orientation (degrees) ===")
print(f"Roll:  {math.degrees(roll):.3f}")
print(f"Pitch: {math.degrees(pitch):.3f}")
print(f"Yaw:   {math.degrees(yaw):.3f}")

# 4) GPS
gps = client.getGpsData(vehicle_name=vehicle_name)
gp = gps.gnss.geo_point

print("\n=== GPS (Geopoint) ===")
print(f"Latitude:  {gp.latitude}")
print(f"Longitude: {gp.longitude}")
print(f"Altitude:  {gp.altitude}")

print("\n=== Summary ===")
print(f"NED (m):   {p_est.x_val:.2f}, {p_est.y_val:.2f}, {p_est.z_val:.2f}")
print(f"GPS:       {gp.latitude:.8f}, {gp.longitude:.8f}, alt={gp.altitude:.2f}")

print("\nDone.")