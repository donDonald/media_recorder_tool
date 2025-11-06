#!/bin/bash

usage() {
    echo "To capture streams: ./Container.sh [streams setup] capture" 1>&2
    echo "To pack streams into streams: ./Container.sh [streams setup] create [mp4|mkv]" 1>&2
}




INPUT=$1
if [ -z $INPUT ]; then
    echo "Where is streams setup? Exiting" 1>&2
    usage
    exit 1
fi

if [ ! -f $INPUT ]; then
    echo "Assigned streams setup doen not exist. Exiting" 1>&2
    exit 1
fi

OUTPUT="tmp.$INPUT"




CMD=$2
if [ -z $CMD ]; then
    echo "Where is command? Exiting" 1>&2
    usage
    exit 1
fi


if [ $CMD = "create" ]; then
    CONTAINER=$3
    if [ -z $CONTAINER ]; then
        echo "Where is container type? Use [mp4, mkv]. Exiting" 1>&2
        exit 1
    fi
    case "$CONTAINER" in
        "mp4")
            echo "Using mp4 container"
            ;;
        "mkv")
            echo "Using mkv container"
            ;;
        *)
            echo "Unknown container type, use [mp4, mkv]. Exiting" 1>&2
            exit 1
            ;;
    esac
fi




# Collect the streams
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.* || -z "$key" ]] && continue

    # Trim whitespace from key and value (optional)
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Process the key-value pair
#   echo "Key: $key, Value: $value"

    # You can also assign them to variables dynamically
    declare "$key=$value"
done < $INPUT

MAX_TRACK_COUNT=33
declare -a STREAMS
for (( i=0; i<$MAX_TRACK_COUNT; i++ )); do
    TYPE="TRACK_${i}_TYPE"
    DEVICE="TRACK_${i}_DEVICE"
    NAME="TRACK_${i}_NAME"
    COMMAND="TRACK_${i}_COMMAND"
    if [[ -v $TYPE ]]; then
        TYPE_V=${!TYPE}
        DEVICE_V=${!DEVICE}
        NAME_V=${!NAME}
        COMMAND_V=${!COMMAND}
#       echo "TYPE_V:$TYPE_V"
#       echo "DEVICE_V:$DEVICE_V"
#       echo "NANE_V:$NAME_V"
#       echo "COMMAND_V:$COMMAND_V"
        STREAMS+=("$TYPE_V;$DEVICE_V;$NAME_V;$COMMAND_V")
    fi
done
STREAMS_COUNT=${#STREAMS[@]}
echo "Total amount of streams:$STREAMS_COUNT"
echo "Streams:"
for STREAM in "${STREAMS[@]}"; do
    echo "$STREAM"
done





case "$CMD" in
    "capture")
        echo "Capture streams"
            # Capture streams
            rm -rf $OUTPUT && mkdir -p $OUTPUT

            for STREAM in "${STREAMS[@]}"; do
                echo "STREAM:$STREAM"
                declare -a OPTIONS
                OPTIONS=()
                OLDIFS="$IFS"
                IFS=';'
                for opt in $STREAM; do
                    OPTIONS+=($opt)
                done
                IFS="$OLDIFS"

                TYPE=${OPTIONS[0]}
                DEVICE=${OPTIONS[1]}
                NAME=${OPTIONS[2]}
                COMMAND=${OPTIONS[3]}
            #   echo "TYPE:$TYPE, DEVICE:$DEVICE, NAME:$NAME, COMMAND:$COMMAND"

                if [ "audio" == $TYPE ]; then
                    echo "Append audio track, DEVICE:$DEVICE, NAME:$NAME, COMMAND:$COMMAND"
                    (./AudioRecorder.sh "$OUTPUT/$NAME" $DEVICE $COMMAND &)
                elif [ "video" == $TYPE ]; then
                    echo "Append video track, DEVICE:$DEVICE, NAME:$NAME, COMMAND:$COMMAND"
                    (./VideoRecorder.sh "$OUTPUT/$NAME" mpeg $DEVICE $COMMAND &)
                fi
            done
        ;;
    "create")
        echo "Create container"
        STREAM_INDEX=0
        STREAM_INPUTS=""
        STREAM_MAPS=""
        for STREAM in "${STREAMS[@]}"; do
            echo "STREAM:$STREAM"
            declare -a OPTIONS
            OPTIONS=()
            OLDIFS="$IFS"
            IFS=';'
            for opt in $STREAM; do
                OPTIONS+=($opt)
            done
            IFS="$OLDIFS"

            TYPE=${OPTIONS[0]}
            DEVICE=${OPTIONS[1]}
            NAME=${OPTIONS[2]}
            COMMAND=${OPTIONS[3]}
            CONTAINER_NAME="$INPUT.$CONTAINER"
           #echo "TYPE:$TYPE, DEVICE:$DEVICE, NAME:$NAME, COMMAND:$COMMAND"
           #echo "CONTAINER_NAME:$CONTAINER_NAME"
            if [ "audio" == $TYPE ]; then
                echo "Append audio track, DEVICE:$DEVICE, NAME:$NAME, COMMAND:$COMMAND"
                TRACK=$OUTPUT/$NAME.mp3
                echo "TRACK:$TRACK"
                STREAM_INPUTS+=" -i $TRACK"
                STREAM_MAPS+=" -map $STREAM_INDEX:a"
                echo "STREAM_INPUTS:$STREAM_INPUTS"
                echo "STREAM_MAPS:$STREAM_MAPS"
            elif [ "video" == $TYPE ]; then
                echo "Append video track, DEVICE:$DEVICE, NAME:$NAME, COMMAND:$COMMAND"
                TRACK=$OUTPUT/$NAME.hev1.mpeg
                echo "TRACK:$TRACK"
                STREAM_INPUTS+=" -i $TRACK"
                STREAM_MAPS+=" -map $STREAM_INDEX:v"
                echo "STREAM_INPUTS:$STREAM_INPUTS"
                echo "STREAM_MAPS:$STREAM_MAPS"
            fi
            ((++STREAM_INDEX))
        done

        echo "STREAM_INPUTS:$STREAM_INPUTS"
        echo "STREAM_MAPS:$STREAM_MAPS"
        FF_PARAMS="$STREAM_INPUTS $STREAM_MAPS -c copy $CONTAINER_NAME"
        echo "FF_PARAMS:$FF_PARAMS"

        # Convert the string to an array
        IFS=' ' read -r -a my_params_array <<< "$FF_PARAMS"
        ffmpeg "${my_params_array[@]}"
        if [ $? -eq 0 ]; then
            echo "Command succeeded"
            echo "$CONTAINER container saved as $CONTAINER_NAME"
        else
            echo "Command failed with exit status: $?"
        fi
        exit $?
        ;;
    *)
        echo "Unknown CMD:$CMD, use [create]. Exiting" 1>&2
        exit 1
        ;;
esac




#   ffmpeg -i input_video.mp4 -i new_audio.mpmp3 -map 0:v -map 0:a -map 1:a -c copy output_video_with_multiple_audio.mp4
#   Explanation of the command:

#       ffmpeg: Invokes the FFmpeg program.
#       -i input_video.mp4: Specifies the primary input file, which contains the original video and audio. This is referred to as input 0.
#       -i new_audio.mp3: Specifies the secondary input file, which is the new audio track to be added. This is referred to as input 1.
#       -map 0:v: Selects all video streams from the first input (input_video.mp4).
#       -map 0:a: Selects all audio streams from the first input (input_video.mp4), preserving the original audio.
#       -map 1:a: Selects all audio streams from the second input (new_audio.mp3), adding the new audio track.
#       -c copy: Instructs FFmpeg to stream-copy the selected streams without re-encoding, which preserves the original quality and speeds up the process.
#       output_video_with_multiple_audio.mp4: Specifies the name of the output file containing the video with both audio tracks.

#   Important Considerations:

#       Stream Indexing:
#       If there are multiple video or audio streams within a single input file, specific streams can be selected using 0:v:0 for the first video stream of the first input, 0:a:1 for the second audio stream of the first input, and so on.
#       Audio Codecs:
#       If the audio codecs are different between the original and new audio tracks, or if a specific output format requires a particular audio codec, re-encoding may be necessary. In such cases, replace -c copy with appropriate codec options like -c:v copy -c:a aac.
#       Synchronization:
#       If the new audio track is not perfectly synchronized with the video, options like -itsoffset can be used to introduce a delay to the audio stream.
