# Autonomous Drone Navigation (UE5 + Cesium + Cosys-AirSim + Python)

This project simulates an autonomous drone mission in a realistic urban environment. The mission runs inside **Unreal Engine 5.2.1**, uses **Cesium** to stream a real-world 3D map of **Genova**, relies on **Cosys-AirSim** for multirotor simulation and API control, uses **Blueprints** to extract/debug waypoint and drone coordinates, and uses **Python** to execute the autonomous navigation logic.

<p align="center">
  <img src="docs/images/01-project-cover.png" alt="Autonomous Drone Navigation cover" width="850" />
</p>

> Report / presentation source: **Virtual Reality for Robotics - Autonomous Drone Navigation** (A.Y. 2025-2026)

## Group members

| Name Surname | ID | Email address |
| ------------ | -- | ------------- |
| [Sayna Arghideh](https://github.com/Arghidehsayna) | S5934809 | S5934809@studenti.unige.it |
| [Mahnaz Mohammad Karimi](https://github.com/ALFA-PM) | S6212087 | S6212087@studenti.unige.it |
| [Alireza Tajabadi Farahani](https://github.com/ALFA-PM) | S6212483 | S6212483@studenti.unige.it |
| [AmirMahdi Matin](https://github.com/amirmat98) | S5884715 | S5884715@studenti.unige.it |

## Supervisors

- [Gianni Vercelli](https://rubrica.unige.it/personale/VUZCWVtr)
- [Saverio Iacono](https://rubrica.unige.it/personale/U0tGXV1h)

## Mission Goals

The drone must:
- take off and climb to a safe altitude above the urban scene,
- navigate building-to-building using waypoint actors defined in Unreal Engine,
- stop at each target building and print delivery logs,
- perform a painting-like vertical motion at one selected building,
- detect a forbidden zone and stop before entering it,
- end the mission safely in hover.

## System Overview

The project is built around four main components:
- **Unreal Engine 5.2.1** for the 3D simulation environment,
- **Cesium for Unreal** for real-world 3D map streaming,
- **Cosys-AirSim** for drone simulation and API access,
- **Python** for mission execution and safety logic.

<p align="center">
  <img src="docs/images/02-cesium-genova.png" alt="Cesium real-world 3D map of Genova in Unreal Engine" width="850" />
</p>

## Tools & Technologies

- **Unreal Engine 5.2.1**  
  Real-time 3D engine used to build the environment and run the simulation.
- **Cesium for Unreal**  
  Streams photorealistic 3D tiles, terrain, and geographic data into the Unreal scene.
- **Cosys-AirSim**  
  Unreal Engine plugin based on Microsoft AirSim, used to simulate the multirotor and expose Python/C++ APIs.
- **Blueprints**  
  Visual scripting used to discover actors, read positions, and print waypoint/drone data at runtime.
- **Python (Cosys-AirSim API)**  
  Used to connect to the drone, arm it, take off, move between waypoints, and apply mission logic.

## Main Simulation Scene

The mission is executed in a realistic urban environment generated through Cesium and simulated inside Unreal Engine.

<p align="center">
  <img src="docs/images/03-live-simulation.png" alt="Live simulation demonstration in Unreal Engine" width="850" />
</p>

## Waypoint Definition in Unreal Engine

Target buildings are defined directly inside Unreal Engine using **Actors**:
- waypoint actors are manually placed in the level,
- each waypoint is renamed (`wp_01`, `wp_02`, ..., `wp_06`),
- each one is tagged with **`Wp`** so it can be found automatically.

<p align="center">
  <img src="docs/images/04-waypoint-actors.png" alt="Waypoint actors placed and tagged in Unreal Engine" width="850" />
</p>

## Blueprint-Based Data Extraction

A Blueprint is used to:
- get all actors in the level,
- filter actors by the **`Wp`** tag,
- retrieve waypoint names and world coordinates `(X, Y, Z)`,
- retrieve the drone origin from `BP_FlyingPawn`,
- print both waypoint and drone coordinates for debugging and later Python use.

<p align="center">
  <img src="docs/images/05-blueprint-waypoint-drone.png" alt="Blueprint for waypoint and drone position extraction" width="850" />
</p>

## Forbidden Zone Visualization

A dedicated material is used to make the no-fly area visible in the map:
- the material uses a **red base color**, 
- opacity is set to **0.5**, 
- blend mode is set to **Translucent**.

This makes the forbidden volume easy to see while keeping the environment visible through it.

<p align="center">
  <img src="docs/images/06-forbidden-zone-material.png" alt="Forbidden zone material in Unreal Engine" width="850" />
</p>

## Python Drone Control

The Python side uses the **Cosys-AirSim API** for initialization and basic flight control.

Typical first steps are:

```bash
pip install cosys-airsim
```

Typical API flow:

```python
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.hoverAsync().join()
client.moveToZAsync(-20, 2).join()
```

Notes:
- default drone name: **`Drone1`**
- coordinate system: **NED**
  - `X = North`
  - `Y = East`
  - `Z = Down`

<p align="center">
  <img src="docs/images/07-python-control.png" alt="Python drone control setup slide" width="850" />
</p>

## Project Files / Code Reference

The Python mission logic is organized into separate scripts:
- `python/start.py` - main entry point,
- `python/connect.py` - AirSim connection, API control, and arming,
- `python/takeoff.py` - takeoff, stabilization, and move to safe altitude,
- `python/waypoint3.py` - final mission logic: waypoint traversal, forbidden-zone checks, painting behavior, safe stop, and end-of-mission hover.

> Folder reference: all controller scripts are in the **`python/`** folder.

## How to Run

### 1) Open the Unreal project
1. Open `newproject.uproject`.
2. Load the final mission map / level.
3. Make sure the Cesium scene and AirSim drone are present.
4. Press **Play**.

### 2) Verify the required plugins
In **Edit -> Plugins**, verify that the following are enabled:
- **Cesium for Unreal**
- **Cosys-AirSim**
- **AirSim**

Restart Unreal Engine if requested.

### 3) Run the Python mission controller
After the Unreal simulation is running:

```bash
pip install cosys-airsim
python python/start.py
```

## Autonomous Navigation Logic

The mission flow is:

1. **Initialization**  
   Connect to AirSim, enable API control, arm the drone, and take off.

2. **Read Waypoints**  
   Retrieve waypoint positions from Unreal and compute the target building heights.

3. **Compute Safe Altitude**  
   Calculate a global `SAFE_Z` above all buildings and move there before the mission starts.

4. **Waypoint Navigation**  
   For each waypoint:
   - compute the commanded altitude,
   - check forbidden-zone safety,
   - fly and hover if safe,
   - stop and hold if unsafe.

5. **Painting / Delivery Behavior**  
   At every building the system prints delivery information, and at one selected building it performs a short vertical painting-like motion.

6. **Forbidden Zone Preview**  
   Preview the next target before moving; if the move is unsafe, stop the mission.

7. **Mission End**  
   Hold position safely and print mission status / delivery logs.
