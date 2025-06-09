#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <script_name>"
  exit 1
fi

SCRIPT_NAME="$1"
HANDLER_FILE="${SCRIPT_NAME}_script.py"
SCRIPT_DIR="scripts/${SCRIPT_NAME}"
BUILD_DIR="build/function"
ZIP_FILE="${SCRIPT_NAME}.zip"

# sanity checks
if [ ! -f "${SCRIPT_DIR}/${HANDLER_FILE}" ]; then
  echo "ERROR: Cannot find ${SCRIPT_DIR}/${HANDLER_FILE}"
  exit 1
fi

# clean & prepare
rm -rf "${BUILD_DIR}" "${ZIP_FILE}"
mkdir -p "${BUILD_DIR}"

# copy handler
cp "${SCRIPT_DIR}/${HANDLER_FILE}" "${BUILD_DIR}/"

# zip
(
  cd "${BUILD_DIR}"
  zip -r9 "../../${ZIP_FILE}" .
)

echo "[✓] Packaged function → ${ZIP_FILE}"

