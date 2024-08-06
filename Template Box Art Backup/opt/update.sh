#!/bin/sh

PROCESS_FILES() {
    DIR_PATH="$1"

    echo "Processing files in $DIR_PATH..." >/tmp/muxlog_info

    # First pass: Delete non-newboxart.* files
    find "$DIR_PATH" -type f -print0 | while IFS= read -r -d '' FILE; do
        BASENAME=$(basename "$FILE")
        case "$BASENAME" in
            newboxart.*)
                # Do nothing, we will handle these in the next pass
                ;;
            *)
                rm -f "$FILE"
                echo "Deleted $FILE" >/tmp/muxlog_info
                ;;
        esac
    done

    # Second pass: Rename newboxart.* files
    find "$DIR_PATH" -type f -print0 | while IFS= read -r -d '' FILE; do
        BASENAME=$(basename "$FILE")
        DIRNAME=$(dirname "$FILE")
        case "$BASENAME" in
            newboxart.*)
                NEWNAME="${BASENAME#newboxart.}"
                mv "$FILE" "$DIRNAME/$NEWNAME"
                echo "Renamed $FILE to $DIRNAME/$NEWNAME" >/tmp/muxlog_info
                ;;
        esac
    done

    echo "Files processed in $DIR_PATH" >/tmp/muxlog_info
}

PROCESS_FILES "/mnt/mmc/MUOS/info/catalogue"

echo "Sync filesystem" >/tmp/muxlog_info
sync
