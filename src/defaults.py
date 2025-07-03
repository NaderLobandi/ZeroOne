import json
from jsonschema import validate, ValidationError

# Default values in case LLM does not provide them
DEFAULTS = {
    "room_dimensions": [400, 500, 300],        # width, length, height
    "bedside_table_dimensions": [50, 50, 75],  
    "lamp_dimensions": [20, 20, 40],           
    "skylight_dimensions": [100, 100, 10]    
}


def sanitize_scene_graph(scene):
    """
    Fills in missing values (dimensions, positions) based on parametric relationships. (For Bonus pointS)
    """
    # Get rooms and objects by ID
    rooms_by_id = {r["id"]: r for r in scene.get("rooms", [])}
    objects_by_id = {o["id"]: o for o in scene.get("objects", [])}

    # Normalize rooms
    for room in rooms_by_id.values():
        if "dimensions_cm" not in room:
            room["dimensions_cm"] = DEFAULTS["room_dimensions"]

    # Normalize objects
    for obj in scene.get("objects", []):
        # Set default dimensions if missing
        if "dimensions_cm" not in obj:
            if obj["type"] == "lamp":
                obj["dimensions_cm"] = DEFAULTS["lamp_dimensions"]
            elif obj["type"] == "bedside_table":
                obj["dimensions_cm"] = DEFAULTS["bedside_table_dimensions"]
            elif obj["type"] == "skylight":
                obj["dimensions_cm"] = DEFAULTS["skylight_dimensions"]

        # Set position parametric to parent
        if "position_cm" not in obj:
            parent_id = obj.get("parent")
            parent = objects_by_id.get(parent_id) or rooms_by_id.get(parent_id)

            if not parent:
                print(f"⚠️ Warning: Parent '{parent_id}' not found for object '{obj['id']}'")
                continue

            pw, pl, ph = parent.get("dimensions_cm", DEFAULTS["room_dimensions"])
            ow, ol, oh = obj.get("dimensions_cm", [0, 0, 0])

            # Object-specific logic
            if obj["type"] == "lamp":
                # Center lamp on top of parent surface
                obj["position_cm"] = [
                    pw / 2 - ow / 2,
                    pl / 2 - ol / 2,
                    ph 
                ]

            elif obj["type"] == "skylight":
                # Center skylight on top of room
                obj["position_cm"] = [
                    pw / 2 - ow / 2,
                    pl / 2 - ol / 2,
                    ph 
                ]

            else:
                # Default is to place on floor
                obj["position_cm"] = [0, 0, 0]

    return scene


def validate_scene_graph(scene, schema):
    """
    Validates the scene graph against our defined JSON schema.
    """
    try:
        validate(instance=scene, schema=schema)
        print("Scene graph is valid.")
        return True
    except ValidationError as e:
        print("Scene graph failed validation:")
        print(e)
        return False
