# Autonomous Drone Navigation (UE5 + Cesium + Cosys-AirSim + Python)

This project simulates an autonomous drone mission in a realistic urban environment. The mission runs inside **Unreal Engine 5.2.1**, using **Cesium** to stream a 3D city map, **Cosys-AirSim** for multirotor simulation and API control, **Blueprints** to export/debug waypoints, and **Python** to execute the navigation logic.  
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
- **Unreal Engine 5.2.1**  
  https://www.unrealengine.com/en-US
- **Cesium Photorealistic 3D Tiles (learning page / reference)**  
  https://cesium.com/learn/cesiumjs-learn/cesiumjs-photorealistic-3d-tiles/
- **Cosys-AirSim (simulation + Python API)**  
  https://github.com/Cosys-Lab/Cosys-AirSim

Additional components used:
- **Blueprints (BP_WaypointExporter)**: prints waypoint names and world positions at runtime for validation/export.
- **Python (AirSim API Controller)**: mission controller (connect, takeoff, safe altitude, waypoint traversal, painting, forbidden zone checks, safe stop/hover).

## Project Files / Code Reference

The Python mission logic is organized into separate scripts (used as reference for the controller flow):
- `python/start.py` — main entry point (runs the mission sequence)
- `python/connect.py` — AirSim connection + API control + arming
- `python/takeoff.py` — takeoff + stabilization + move to safe altitude
- `python/waypoint3.py` — final mission logic (navigation, painting, forbidden-zone stop, safe hover/end)

> Folder reference: all controller scripts are in the **`python/`** folder.

## How to Run (Unreal + Python)

### 1) Run the Unreal Project
1. Open **`newproject.uproject`**
2. In Unreal Engine, open the **Level** and choose **Final Map** (the final mission map used in the report).
3. Press **Play** to start the simulation (AirSim must be active in the level).

### 2) Enable / Verify Plugins (Unreal Engine)
1. Go to: **Edit → Plugins**
2. Search and enable:
   - **Cosys-AirSim** (Cosys plugin)
   - **AirSim**
   - (and Cesium plugin if your project uses it in the level)
3. Restart Unreal Engine if prompted.

> You can also locate related plugin content inside Unreal using the **Content Drawer** (enable “Show Plugin Content” if you don’t see it).

### 3) Run the Python Controller
After the Unreal simulation is running, execute:

```bash
python code/start.py
