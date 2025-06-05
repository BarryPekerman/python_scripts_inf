#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./package.sh <script_name> (e.g., wikipedia)"
  exit 1
fi

SCRIPT_NAME=$1
SCRIPT_DIR="scripts/$SCRIPT_NAME"
HANDLER_FILE="${SCRIPT_NAME}_script.py"

if [ ! -f "$SCRIPT_DIR/$HANDLER_FILE" ]; then
  echo "Error: $HANDLER_FILE not found in $SCRIPT_DIR"
  exit 1
fi

echo "[*] Cleaning previous build..."
mkdir -p build

echo "[*] Installing dependencies for $SCRIPT_NAME..."
pip install --target build -r "$SCRIPT_DIR/requirements.txt"

echo "[*] Copying handler..."
cp "$SCRIPT_DIR/$HANDLER_FILE" "build/"

echo "[*] Zipping package..."
cd build
zip -r9 ../${SCRIPT_NAME}.zip .
cd ..

echo "[✓] Packaged $SCRIPT_NAME to ${SCRIPT_NAM}.zip"
echo "Lambda handler should be set to: ${SCRIPT_NAME}_script.lambda_handler"

