#!/bin/bash
# Helper script to compile all "*.po" files to "*.mo" files
ROOT_DIR="$(dirname "$0")"

echo "Search directory: '${ROOT_DIR}'"
find "${ROOT_DIR}" -type f -iname "*.po" -print0 | while IFS= read -r -d $'\0' PO_FILE; 
do
    echo "Compiling: '${PO_FILE}'"
    MO_FILE="${PO_FILE:0:-3}.mo"
    msgfmt -o "${MO_FILE}" "${PO_FILE}"
done
echo "Done."
