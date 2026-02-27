import math
import cosysairsim as airsim

client = airsim.MultirotorClient(ip="127.0.0.1")
client.confirmConnection()

vehicle_name = "Drone1"
print("Connected!\n")

# -----------------------------
# 1) Estimated state (NED, meters)
# -----------------------------
state = client.getMultirotorState(vehicle_name=vehicle_name)
p_est = state.kinematics_estimated.position

print("=== Kinematics Estimated (NED, meters) ===")
print(f"X (North): {p_est.x_val}")
print(f"Y (East):  {p_est.y_val}")
print(f"Z (Down):  {p_est.z_val}")

# -----------------------------
# 2) Ground truth kinematics (NED, meters) - if supported
# -----------------------------
try:
    kin_gt = client.simGetGroundTruthKinematics(vehicle_name=vehicle_name)
    p_gt = kin_gt.position

    print("\n=== Ground Truth Kinematics (NED, meters) ===")
    print(f"X (North): {p_gt.x_val}")
    print(f"Y (East):  {p_gt.y_val}")
    print(f"Z (Down):  {p_gt.z_val}")
except Exception as e:
    print("\n(simGetGroundTruthKinematics not available or failed)")
    print("Error:", e)

# -----------------------------
# 3) Vehicle pose (NED, meters)
# -----------------------------
try:
    pose = client.simGetVehiclePose(vehicle_name=vehicle_name)
    p_pose = pose.position

    print("\n=== simGetVehiclePose Position (NED, meters) ===")
    print(f"X (North): {p_pose.x_val}")
    print(f"Y (East):  {p_pose.y_val}")
    print(f"Z (Down):  {p_pose.z_val}")

    # Orientation -> roll/pitch/yaw
    roll, pitch, yaw = airsim.to_eularian_angles(pose.orientation)

    print("\n=== Orientation (degrees) ===")
    print(f"Roll:  {math.degrees(roll)}")
    print(f"Pitch: {math.degrees(pitch)}")
    print(f"Yaw:   {math.degrees(yaw)}")

except Exception as e:
    print("\n(simGetVehiclePose not available or failed)")
    print("Error:", e)

# -----------------------------
# 4) GPS (world / Cesium), if enabled in settings + vehicle has GPS
# -----------------------------
try:
    gps = client.getGpsData(vehicle_name=vehicle_name)
    gp = gps.gnss.geo_point

    print("\n=== GPS (Geopoint) ===")
    print(f"Latitude:  {gp.latitude}")
    print(f"Longitude: {gp.longitude}")
    print(f"Altitude:  {gp.altitude}")
except Exception as e:
    print("\n(getGpsData not available or GPS not enabled)")
    print("Error:", e)

# -----------------------------
# 5) Unreal-unit conversion hint
# NED meters -> centimeters (Unreal units)
# -----------------------------
print("\n=== NED meters -> Unreal centimeters (just unit conversion) ===")
print(f"X_cm: {p_est.x_val * 100.0}")
print(f"Y_cm: {p_est.y_val * 100.0}")
print(f"Z_cm: {p_est.z_val * 100.0}")

print("\nDone.")