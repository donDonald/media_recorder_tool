#!/bin/bash

OUTPUT=$1
if [ -z $OUTPUT ]; then
    # List avaliable devices if no params ara given
    ./AudioRecorder.py
    exit 1
fi

DEVICE=${2:-"0"}

if [[ -z "${RECORDER_COMMAND}" ]]; then
    COMMAND=${3:-"pause"}
else
    COMMAND=${RECORDER_COMMAND}
fi

./AudioRecorder.py -v0 --device=$DEVICE --command=$COMMAND $OUTPUT.mp3
