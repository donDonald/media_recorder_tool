#!/bin/bash

OUTPUT=$1
if [ -z $OUTPUT]; then
    echo "Where is output name dude? Exiting" 1>&2
    exit
fi

DEVICE=${2:-"0"}

if [[ -z "${RECORDER_COMMAND}" ]]; then
    COMMAND=${3:-"pause"}
else
    COMMAND=${RECORDER_COMMAND}
fi

./AudioRecorder.py -v0 --device=$DEVICE --command=$COMMAND $OUTPUT.mp3
