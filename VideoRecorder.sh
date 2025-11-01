#!/bin/bash

OUTPUT=$1
if [ -z $OUTPUT ]; then
    echo "Where is output name dude? Exiting" 1>&2
    exit 1
fi


CONTAINER=$2
if [ -z $CONTAINER ]; then
    echo "Where is container type dude? Use [mp4, mkv, mpeg]. Exiting" 1>&2
    exit 1
fi
case "$CONTAINER" in
    "mp4")
        echo "Using mp4 container"
        ;;
    "mkv")
        echo "Using mkv container"
        ;;
    "mpeg")
        echo "Using mpeg raw stream"
        ;;
    *)
        echo "Unknown container type, use [mp4, mkv, mpeg]. Exiting" 1>&2
        exit 1
        ;;
esac

DEVICE=${3:-"0"}

if [[ -z "${RECORDER_COMMAND}" ]]; then
    COMMAND=${4:-"pause"}
else
    COMMAND=${RECORDER_COMMAND}
fi

FORMAT=${5:-"MJPG"}
FORMAT=${5:-"FMP4"}
FORMAT=${5:-"mp4v"}
FORMAT=${5:-"XVID"}
FORMAT=${5:-"DIVX"}
FORMAT=${5:-"avc1"}
FORMAT=${5:-"hvc1"}
FORMAT=${5:-"vp09"}
FORMAT=${5:-"hev1"}

./VideoRecorder.py -v1 --device=$DEVICE --wwidth=960 --wheight=540 --fps=24 --oformat=$FORMAT --command=$COMMAND $OUTPUT.$FORMAT.$CONTAINER
