#!/bin/bash

echo "=============================="
echo "Running ZeroOne Demo Script"
echo "=============================="

# Abort on any error
set -e

# Define absolute paths (adjust as needed)
UE_PATH="/Users/Shared/Epic Games/UE_5.6/Engine/Binaries/Mac/UnrealEditor"
PROJECT_PATH="$HOME/Desktop/ZeroOne/ZeroOne/ZeroOne.uproject"
SCRIPT_PATH="$HOME/Desktop/ZeroOne/unreal/BuildScene.py"
VENV_PATH="$HOME/Desktop/ZeroOne/venv"
REQ_PATH="$HOME/Desktop/ZeroOne/requirements.txt"
PROMPT_PARSER="$HOME/Desktop/ZeroOne/src/parse_prompt.py"
SCENE_JSON_PATH="$HOME/Desktop/ZeroOne/demo/scene.json"

echo "Step 1: Set up Python virtual environment"
if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install -r "$REQ_PATH"

echo "Step 2: Run prompt → scene parser"
python3 "$PROMPT_PARSER"

if [ ! -f "$SCENE_JSON_PATH" ]; then
  echo "scene.json was not generated. Exiting."
  exit 1
fi

echo "Step 3: Launch Unreal in headless mode"
"$UE_PATH" "$PROJECT_PATH" -run=pythonscript -script="$SCRIPT_PATH" -nullrhi

echo "Step 4: Build complete!"
echo "Check UE project at: /Users/nalo/UnrealProjects/ZeroOne/"
echo "Map saved to: Content/Maps/BlockOut.umap"
