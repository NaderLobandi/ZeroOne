import pytest
from defaults import sanitize_scene_graph, DEFAULTS

# Test1: Room gets default dimensions if missing
def test_room_fills_default_dimensions():
    scene = {
        "rooms": [{"id": "room1", "type": "loft"}],
        "objects": []
    }
    result = sanitize_scene_graph(scene)
    assert result["rooms"][0]["dimensions_cm"] == DEFAULTS["room_dimensions"]

# Test2: Lamp gets centered on top of table
def test_lamp_position_is_parametric():
    scene = {
        "rooms": [
            {"id": "room1", "type": "loft", "dimensions_cm": [400, 500, 300]}
        ],
        "objects": [
            {
                "id": "table1",
                "type": "bedside_table",
                "parent": "room1",
                "dimensions_cm": [50, 50, 75]
            },
            {
                "id": "lamp1",
                "type": "lamp",
                "parent": "table1",
                "dimensions_cm": [20, 20, 40]
            }
        ]
    }

    result = sanitize_scene_graph(scene)
    lamp = next(o for o in result["objects"] if o["id"] == "lamp1")

    expected_position = [
        50 / 2 - 20 / 2, 
        50 / 2 - 20 / 2,  
        75      
    ]

    assert lamp["position_cm"] == expected_position

# Test3: Skylight placed at ceiling center
def test_skylight_position_is_parametric():
    scene = {
        "rooms": [
            {"id": "room1", "type": "loft", "dimensions_cm": [400, 500, 300]}
        ],
        "objects": [
            {
                "id": "skylight1",
                "type": "skylight",
                "parent": "room1",
                "dimensions_cm": [100, 100, 10]
            }
        ]
    }

    result = sanitize_scene_graph(scene)
    skylight = result["objects"][0]

    expected_position = [
        400 / 2 - 100 / 2,
        500 / 2 - 100 / 2,
        300 
    ]

    assert skylight["position_cm"] == expected_position

# Test4: Missing parent handled gracefully with a warning to user
def test_missing_parent_does_not_crash(capfd):
    scene = {
        "rooms": [{"id": "room1", "type": "loft"}],
        "objects": [
            {
                "id": "lamp1",
                "type": "lamp",
                "parent": "nonexistent_parent"
            }
        ]
    }

    result = sanitize_scene_graph(scene)

    out, _ = capfd.readouterr()
    assert "Parent 'nonexistent_parent' not found for object 'lamp1'" in out

    # Ensure object doesn't have a position (no parent assumed)
    lamp = result["objects"][0]
    assert "position_cm" not in lamp
