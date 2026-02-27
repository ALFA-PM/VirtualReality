# Autonomous Drone Navigation (UE5 + Cesium + Cosys-AirSim + Python)

This project simulates an autonomous drone mission in a realistic urban environment. The mission runs inside **Unreal Engine 5.2.1**, using **Cesium for Unreal** to stream a 3D city map, **Cosys-AirSim** for multirotor simulation and API control, **Blueprints** to export/debug waypoints, and **Python** to execute the navigation logic.  
(Report: *Autonomous Drone Navigation – Virtual Reality for Robotics*, A.Y. 2025–2026)  

## Mission Goals
The drone must:
- Take off and climb to a safe height above obstacles.
- Navigate building-to-building using user-placed waypoints (authored in Unreal Engine).
- Stop at each target building and print logs (e.g., **"Color Delivered"**).
- Perform a **painting** behavior at one selected building (vertical sweep).
- Detect a **Forbidden Zone** (no-fly volume) and stop before entering it.
- End the mission safely in a stable hover.

## Tools & Technologies
- **Unreal Engine 5.2.1**: level setup, waypoints, collision meshes, forbidden zone volumes, blueprint logic.
- **Cesium for Unreal**: streamed 3D city tiles (example location used in report: Genova).
- **Cosys-AirSim**: UE plugin providing multirotor physics simulation + Python API control.
- **Blueprints (BP_WaypointExporter)**: prints waypoint names and world positions at runtime for validation/export.
- **Python (AirSim API Controller)**: mission controller (connect, takeoff, safe altitude, waypoint traversal, painting, forbidden zone checks, safe stop/hover).

## How It Works

### 1) Waypoints (Unreal Engine)
- Waypoints are placed manually as actors in the UE level.
- They are named sequentially (example: `wp_01 ... wp_08`) to define mission order.
- They are tagged (example tag: `Wp`) so they can be found programmatically.

### 2) Waypoint Export & Debug (Blueprint)
A Blueprint actor **BP_WaypointExporter** runs on `BeginPlay`:
- Collects all waypoint actors
- Filters them by tag (e.g., `Wp`)
- Prints each waypoint name and world location `(X, Y, Z)` for debugging and verification

> Note: Unreal coordinates are **centimeters** and **Z-up**.

### 3) Coordinate Conversion (UE → AirSim)
Before navigation, waypoint locations are converted:
- **Unreal Engine**: cm, Z-up  
- **AirSim NED**: meters, Z-down  

This conversion must be applied consistently for:
- waypoint navigation
- forbidden zone checks

### 4) Python Drone Controller (AirSim API)
The Python mission is a finite sequence:
1. **Initialization**
   - Connect to AirSim
   - Enable API control and arm
   - Take off and wait until stable
2. **Safe Altitude Policy**
   - Move to a global safe cruise altitude `SAFE_Z` (NED frame)
   - Because NED is z-down, **higher altitude = more negative z**
3. **Waypoint Navigation**
   For each waypoint (in name order):
   - Read waypoint position (already converted to NED)
   - Set commanded altitude `zcmd` (usually `SAFE_Z`)
   - Move to `(xned, yned, zcmd)`
   - Hover briefly to stabilize
4. **Delivery Logging**
   - At each waypoint, print a message such as **"Color Delivered"**
5. **Painting Behavior**
   - At one selected waypoint, perform a vertical sweep along NED z-axis:
     - Downward = increasing z (less negative / more positive)
     - Upward = decreasing z (more negative)
   - Keep the sweep within a safe range/margin to avoid collisions
6. **Forbidden Zone Stopping**
   - Forbidden zone is defined in UE as a box trigger volume.
   - In Python it is modeled as a rotated 3D box defined by:
     - center position
     - extents (half-dimensions)
     - yaw rotation
     - additional safety margin
   - Before moving to the next waypoint, perform:
     - **Target check**: destination inside forbidden volume?
     - **Path check**: segment from current position to destination intersects forbidden volume?
   - If violation is detected:
     - print warning log (e.g., **"Forbidden Zone"**)
     - stop forward progress
     - hover safely and terminate mission

## Expected Results (Simulation)
- Drone connects, takes off, and navigates in the Cesium-streamed city.
- Waypoints authored in UE are used as targets (no manual coordinate typing in Python).
- Safe altitude policy reduces risk near buildings.
- Painting sweep works at the chosen building without collisions under tested conditions.
- Forbidden zone checks stop the drone before entering restricted airspace, with log confirmation.

