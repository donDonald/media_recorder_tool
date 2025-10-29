#!/bin/bash

OUTPUT=$1
if [ -z $OUTPUT]; then
    echo "Where is output name dude? Exiting" 1>&2
    exit
fi

DEVICE=${2:-"0"}

FORMAT=${3:-"MJPG"}
FORMAT=${3:-"FMP4"}
FORMAT=${3:-"mp4v"}
FORMAT=${3:-"XVID"}
FORMAT=${3:-"DIVX"}
FORMAT=${3:-"avc1"}
FORMAT=${3:-"hvc1"}
FORMAT=${3:-"vp09"}
FORMAT=${3:-"hev1"}

if [[ -z "${RECORDER_COMMAND}" ]]; then
    COMMAND=${3:-"pause"}
else
    COMMAND=${RECORDER_COMMAND}
fi

./VideoRecorder.py -v1 --device=$DEVICE --wwidth=960 --wheight=540 --fps=24 --oformat=$FORMAT --command=$COMMAND $OUTPUT.$FORMAT.mkv
