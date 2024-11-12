#!/bin/sh
# HELP: gridcopy
# ICON: gridcopy

. /opt/muos/script/var/func.sh

CORE_DIRECTORY="/run/muos/storage/info/core"
GRID_FOLDER="/run/muos/storage/info/catalogue/Folder/grid"

# Loop through each 'core.cfg' file in CORE_DIRECTORY
find "$CORE_DIRECTORY" -type f -name "core.cfg" | while IFS= read -r CORE_CONFIG; do
    FOLDER_NAME=$(basename "$(dirname "$CORE_CONFIG")")
    SECOND_LINE=$(sed -n '2p' "$CORE_CONFIG")

    LOG_INFO "$0" 0 "" "Processing '%s' (%s)" "$FOLDER_NAME" "$SECOND_LINE"

    if [ -z "$SECOND_LINE" ]; then
        LOG_ERROR "$0" 0 "" "Unable to read core from '%s' or it is empty. Skipping!\n" "$CORE_CONFIG"
        continue
    fi
    
    if [ "$(echo "$GRID_FOLDER/$SECOND_LINE.png" | tr '[:upper:]' '[:lower:]')" = "$(echo "$GRID_FOLDER/$FOLDER_NAME.png" | tr '[:upper:]' '[:lower:]')" ]; then
        LOG_INFO "$0" 0 "" "File already exists %s/%s.png\n" "$GRID_FOLDER" "$FOLDER_NAME"
        continue
    fi

    if [ -f "$GRID_FOLDER/$SECOND_LINE.png" ]; then
        cp -f "$GRID_FOLDER/$SECOND_LINE.png" "$GRID_FOLDER/$FOLDER_NAME.png"
        LOG_INFO "$0" 0 "" "Copied %s.png to %s.png\n" "$SECOND_LINE" "$FOLDER_NAME"
    elif [ -f "$GRID_FOLDER/default.png" ]; then
        cp -f "$GRID_FOLDER/default.png" "$GRID_FOLDER/$FOLDER_NAME.png"
        LOG_INFO "$0" 0 "" "Copied default.png to %s.png\n" "$FOLDER_NAME"
    else
        LOG_WARNING "$0" 0 "" "No image found for '%s'. Skipping!\n" "$FOLDER_NAME"
    fi
done
echo "Sync Filesystem"
sync

echo "All Done!"
sleep 2

exit 0
