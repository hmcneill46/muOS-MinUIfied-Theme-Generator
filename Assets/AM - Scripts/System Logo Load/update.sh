#!/bin/sh
# HELP: gridcopy
# ICON: gridcopy

. /opt/muos/script/var/func.sh

# Define global variables
CORE_DIRECTORY="/run/muos/storage/info/core"
GRID_FOLDER="/run/muos/storage/info/catalogue/Folder/grid"
ASSIGN_JSON="/mnt/mmc/MUOS/info/assign.json"
ASSIGN_FOLDER="/mnt/mmc/MUOS/info/assign"

# Define a function to handle the common logic
copy_image() {
  local source_name=$1
  local folder_name=$2
  
  LOG_INFO "$0" 0 "" "Processing '%s' (%s)" "$folder_name" "$source_name"  
  if [ -z "$source_name" ]; then
      continue
  fi
  
  if [ "$(echo "$GRID_FOLDER/$source_name.png" | tr '[:upper:]' '[:lower:]')" = "$(echo "$GRID_FOLDER/$folder_name.png" | tr '[:upper:]' '[:lower:]')" ]; then
      LOG_INFO "$0" 0 "" "File already exists %s/%s.png\n" "$GRID_FOLDER" "$folder_name"
      continue
  fi

  if [ -f "$GRID_FOLDER/$source_name.png" ]; then
      cp -f "$GRID_FOLDER/$source_name.png" "$GRID_FOLDER/$folder_name.png"
      LOG_INFO "$0" 0 "" "Copied to %s/%s.png\n" "$GRID_FOLDER" "$folder_name"
  fi
}

# Define the root directory
SOURCE_DIRS="/mnt/mmc/roms /mnt/sdcard/roms /mnt/usb/roms"

# Loop through each source directory
for SOURCE_DIR in $SOURCE_DIRS; do
  echo "Processing $SOURCE_DIR..."
  
  # Find all directories recursively under the current SOURCE_DIR
  find "$SOURCE_DIR" -type d | while read -r dir; do
    # Extract just the folder name
    folder_name=$(basename "$dir")
    # Replace the SOURCE_DIR part with the CORE_DIRECTORY
    transformed_path="${dir/$SOURCE_DIR/$CORE_DIRECTORY}"
    
    # Check if 'core.cfg' exists in the transformed path
    if [ -f "$transformed_path/core.cfg" ]; then
      echo "$transformed_path/core.cfg exists"
      SOURCE_NAME=$(sed -n '2p' "$transformed_path/core.cfg")
      copy_image "$SOURCE_NAME" "$folder_name"
      copy_image "${SOURCE_NAME}_focused" "${folder_name}_focused"
    else
      # Convert the folder name to lowercase
      folder_name_lower=$(echo "$folder_name" | tr '[:upper:]' '[:lower:]')

      # Check if the folder name exists as a key in the JSON file and retrieve its value
      value=$(jq -r "if has(\"$folder_name_lower\") then .\"$folder_name_lower\" else empty end" "$ASSIGN_JSON")
      
      if [ -n "$value" ]; then
        ASSIGN_INI="$ASSIGN_FOLDER/$value"

        # Check if the INI file exists
        if [ -f "$ASSIGN_INI" ]; then
          # Extract 'catalogue' value from the [global] section of the INI file
          catalogue=$(awk -F= '/\[global\]/ {found=1} found && $1~/catalogue/ {print $2; exit}' "$ASSIGN_INI")
          
          if [ -n "$catalogue" ]; then
            copy_image "$catalogue" "$folder_name"
            copy_image "${catalogue}_focused" "${folder_name}_focused"
          fi
        fi
      fi
    fi
  done
done

echo "Sync Filesystem"
sync

echo "All Done!"
sleep 2

exit 0
