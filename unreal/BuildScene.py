import unreal
import json

# CONFIG 
SCENE_JSON_PATH = "/Users/nalo/Desktop/ZeroOne/demo/scene.json"
LEVEL_PATH = "/Game/Maps/BlockOut"
BASIC_CUBE = "/Engine/BasicShapes/Cube.Cube"
BASIC_PLANE = "/Engine/BasicShapes/Plane.Plane"
BASIC_CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"

# LOAD SCENE JSON 
with open(SCENE_JSON_PATH, 'r') as f:
    scene_data = json.load(f)

# FIX 1: Check if level exists first to avoid validation error
if not unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH):
    unreal.EditorLevelLibrary.new_level(LEVEL_PATH)
    unreal.log("New level created.")
else:
    unreal.EditorLevelLibrary.load_level(LEVEL_PATH)
    unreal.log("Existing level loaded.")

# CLEAN OLD ACTORS 
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
for actor in all_actors:
    if not isinstance(actor, unreal.WorldSettings):
        unreal.EditorLevelLibrary.destroy_actor(actor)
unreal.log("🧹 Old actors cleaned from the level.")

# HELPERS 
def cm_to_unreal(cm):
    return cm / 100.0

spawned_actors = {}

def spawn_actor(asset_path, id, position_cm, dimensions_cm):
    factory = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not factory:
        unreal.log_error(f"[!] Failed to load asset: {asset_path}")
        return None

    unreal.log(f"[+] Spawning {id} from {asset_path}")
    location = [cm_to_unreal(x) * 100 for x in position_cm]
    scale = [cm_to_unreal(x) for x in dimensions_cm]

    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
        factory,
        unreal.Vector(*location),
        unreal.Rotator(0, 0, 0)
    )

    if actor:
        actor.set_actor_scale3d(unreal.Vector(*scale))
        spawned_actors[id] = actor
        return actor
    else:
        unreal.log_error(f"Failed to spawn actor {id}")
        return None

# BUILD ROOMS 
for room in scene_data.get("rooms", []):
    unreal.log_warning(f"Building room: {room}")
    room_id = room.get("id")
    dims = room.get("dimensions_cm", [400, 500, 300])
    width, depth, height = dims

    spawn_actor(BASIC_PLANE, f"{room_id}_floor", [width/2, depth/2, 0], [width, depth, 1])
    spawn_actor(BASIC_PLANE, f"{room_id}_ceiling", [width/2, depth/2, height], [width, depth, 1])
    spawn_actor(BASIC_CUBE, f"{room_id}_wall_front", [width/2, 0, height/2], [width, 5, height])
    spawn_actor(BASIC_CUBE, f"{room_id}_wall_back", [width/2, depth, height/2], [width, 5, height])
    spawn_actor(BASIC_CUBE, f"{room_id}_wall_left", [0, depth/2, height/2], [5, depth, height])
    spawn_actor(BASIC_CUBE, f"{room_id}_wall_right", [width, depth/2, height/2], [5, depth, height])

# SPAWN OBJECTS 
for obj in scene_data.get("objects", []):
    unreal.log_warning(f"Spawning object: {obj}")
    obj_id = obj["id"]
    obj_type = obj.get("type", "cube")
    position = obj.get("position_cm", [0, 0, 0])
    size = obj.get("dimensions_cm", [50, 50, 50])

    if obj_type == "lamp":
        asset = BASIC_CYLINDER
    else:
        unreal.log_warning(f"Unknown object type '{obj_type}', defaulting to cube.")
        asset = BASIC_CUBE

    actor = spawn_actor(asset, obj_id, position, size)

    # FIX 2: Use correct signature for attach_to_actor
    parent_id = obj.get("parent")
    if parent_id and parent_id in spawned_actors and actor:
        try:
            actor.attach_to_actor(
                spawned_actors[parent_id],
                socket_name=unreal.Name(""),
                location_rule=unreal.AttachmentRule.SNAP_TO_TARGET,
                rotation_rule=unreal.AttachmentRule.SNAP_TO_TARGET,
                scale_rule=unreal.AttachmentRule.KEEP_WORLD,
                weld_simulated_bodies=False
            )

            unreal.log(f"Attached {obj_id} to {parent_id}")
        except Exception as e:
            unreal.log_error(f"Failed to attach {obj_id} to {parent_id}: {e}")

# SAVE LEVEL 
if not unreal.EditorAssetLibrary.does_directory_exist("/Game/Maps"):
    unreal.EditorAssetLibrary.make_directory("/Game/Maps")

unreal.EditorAssetLibrary.save_asset(LEVEL_PATH, only_if_is_dirty=False)
unreal.log("Level saved to /Game/Maps/BlockOut")
