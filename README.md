# ZeroOne: Scene Generator with Unreal Engine & GPT-4

This project takes a natural language prompt and builds a full Unreal Engine block-out scene from it using GPT-4, JSON scene graphs, and Unreal's Python scripting.

---

## Repo Structure

```
/src/parse_prompt.py      # Step 1 - Prompt to scene.json  
/src/defaults.py          # Fills defaults and validates schema  
/src/defaults_UT.py        # 4 unit tests
/unreal/BuildScene.py     # Step 2 - UE5 headless Python script  
/demo/scene.json    # Auto-generated scene from prompt  
/demo/run_demo.sh         # One-click pipeline runner  
/README.md  
/requirements.txt  
```

---

## How It Works

### 1. **Prompt → JSON (GPT-4):**
`parse_prompt.py` uses function-calling to generate a structured `scene.json` with rooms, objects, hierarchy, and dimensions.

### 2. **Defaults + Validation:**
`defaults.py` fills missing fields (e.g., room size, lamp height) and validates against a JSON schema.

### 3. **Build Unreal Level:**
`BuildScene.py` runs in headless Unreal mode to place walls, floors, and object placeholders using Unreal’s built-in primitives.

### 4. **Save Scene:**
The final level is saved as `BlockOut.umap` inside `/Content/Maps`.

---

## Running `BuildScene.py` (Headless Unreal Mode)

To generate the level from your scene JSON without opening the Unreal Editor UI:

### macOS:
```bash
/Applications/Unreal\ Editor.app/Contents/MacOS/UnrealEditor \
  /Users/nalo/Documents/UnrealProjects/ZeroOne/ZeroOne.uproject \
  -run=pythonscript \
  -script="/Users/nalo/Desktop/ZeroOne/unreal/BuildScene.py" \
  -nullrhi
```

---

## One-Click Demo

Run the full pipeline from prompt to `.umap` using:

```bash
bash demo/run_demo.sh
```

This will:
- Install dependencies  
- Run the LLM parser and default filler  
- Call `BuildScene.py` to spawn the scene  

---

## Set-Up Instructions

### 1. Install Unreal Engine **5.3+** 
Tested on Unreal Engine **5.6**

### 2. Enable Python scripting in the editor:
```
Edit > Plugins > Scripting > Python Editor Script Plugin
```

### 3. Clone this repo and set up a virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create a `.env` file in the root:

```ini
OPENAI_API_KEY=sk-...
```

---

## How to Replace the Prompt

To regenerate a new scene:

1. Open `src/parse_prompt.py`
2. Change the value of `PROMPT` to your new scene  
   _(e.g., `"a cosy loft with skylight and rocket-shaped lamp"`)_
3. Run:

```bash
python src/parse_prompt.py
```

4. This will generate a new `/demo/scene.json`.

5. Then run `BuildScene.py` again to regenerate `BlockOut.umap`.

---

## Output

The generated level is saved to:

```
/Content/Maps/BlockOut.umap
```

You can view this by opening the Unreal project and navigating to the Content Browser.

---

## Bonus Implementation Notes

### Parametric Room Sizes (Done)
Implemented in `BuildScene.py`: Each room reads its `dimensions_cm` field directly from the scene JSON, ensuring room extents dynamically reflect input data without using hardcoded values.

### Unit Tests for Defaults / Sanitizer (Done)
`defaults_UT.py` includes unit tests that validate default-filling behavior and schema compliance, ensuring robustness when fields are missing in the LLM-generated scene graph.

### Accurate Rocket Lamp (Work in Progress)
1. **Locate the Model**: The `lamp.obj` file is already in `src/assets/`.

2. **Import into Unreal**:
   - Open Unreal Editor.
   - In the **Content Browser**, right-click and choose **Import to /Game/Meshes/**.
   - Select `lamp.obj` and complete the import.

3. **Update Script**:
   - In `BuildScene.py`, set:
     ```python
     ROCKET_LAMP_ASSET = "/Game/Meshes/lamp.lamp"
     ```
   - Unreal will now use the imported mesh when spawning the rocket lamp.

4. **Regenerate** the scene using the updated mesh by re-running `BuildScene.py`.


### Dockerfile (Not Yet Implemented)
A Dockerfile could automate the setup of Python dependencies and environment. Unreal Editor itself must still be installed locally due to its GUI and licensing constraints.

### Multiple Rooms with Doorways
Not yet implemented. To extend support, loop through `rooms[]` and calculate wall cut-outs where `doorway` objects exist, then boolean-subtract these from wall meshes (requires UE scripting extensions).

### Level-Up Blockout Environment
Consider adding interactive controls, light sources, or tagging system in the JSON for props and navigation hints in future iterations.

---

## Notes

- All scene logic respects Unreal’s default unit of **centimetres**.
- Only built-in primitives (`/Engine/BasicShapes/*`) are used to ensure portability.

## Known macOS Setup Issue (Xcode & Shader Compilation)

If you're running this on **macOS** and get an error like:

Unreal Engine requires Xcode to compile shaders for Metal...

markdown
Copy
Edit

Please follow these steps to fix it:

1. **Make sure Xcode is installed** from the App Store.

2. **Accept the Xcode license**:
   ```bash
   sudo xcodebuild -license accept
Set the correct developer path:

bash
Copy
Edit
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
Verify the path:

bash
Copy
Edit
xcode-select -p
It should return:

bash
Copy
Edit
/Applications/Xcode.app/Contents/Developer
(Optional) Run Unreal Editor once via GUI to allow initial shader compilation:

bash
Copy
Edit
open -a "/Users/Shared/Epic Games/UE_5.6/Engine/Binaries/Mac/UnrealEditor.app"
If the error persists, make sure Command Line Tools are installed:

bash
Copy
Edit
xcode-select --install