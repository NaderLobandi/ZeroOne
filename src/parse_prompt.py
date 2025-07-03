import openai
import json
from dotenv import load_dotenv
import os


function_schema = {
    "name": "generate_scene_graph",
    "description": "Parses a scene prompt into a rigid scene graph JSON.",
    "parameters": {
        "type": "object",
        "properties": {
            "rooms": {
                "type": "array",
                "description": "List of rooms in the scene.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": { "type": "string", "description": "Unique room identifier" },
                        "type": { "type": "string", "description": "Type of room (e.g., loft, bedroom)" },
                        "dimensions_cm": {
                            "type": "array",
                            "description": "Dimensions in cm: width, length, height",
                            "items": { "type": "number" }
                        }
                    },
                    "required": ["id", "type"]
                }
            },
            "objects": {
                "type": "array",
                "description": "List of objects in the scene",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": { "type": "string", "description": "Object identifier" },
                        "type": { "type": "string", "description": "Object type (e.g., table, lamp)" },
                        "shape": { "type": "string", "description": "Shape of object if applicable (e.g., rocket)" },
                        "parent": { "type": "string", "description": "Parent object or room" },
                        "position_cm": {
                            "type": "array",
                            "description": "Position in cm: x, y, z",
                            "items": { "type": "number" }
                        },
                        "dimensions_cm": {
                            "type": "array",
                            "description": "Dimensions in cm: width, depth, height",
                            "items": { "type": "number" }
                        }
                    },
                    "required": ["id", "type", "parent"]
                }
            }
        },
        "required": ["rooms", "objects"]
    }
}


load_dotenv() # load api key from .env file
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = "Give me a cosy loft with a skylight and put a rocket-shaped lamp on the bedside table."

# GPT-4 with function calling
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that generates scene graph JSON for Unreal."},
        {"role": "user", "content": prompt}
    ],
    functions=[function_schema],
    function_call="auto"
)

# Get arguments from function_call
function_args = response.choices[0].message.function_call.arguments
scene_graph = json.loads(function_args)

# Print and save
print(json.dumps(scene_graph, indent=2))

# Save to demo/scene.json
output_path = os.path.join(os.path.dirname(__file__), '..', 'demo', 'scene.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    json.dump(scene_graph, f, indent=2)

print(f"\nScene graph saved to '{output_path}'")