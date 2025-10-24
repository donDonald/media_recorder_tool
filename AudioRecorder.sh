#!/bin/bash

OUTPUT=$1
if [ -z $OUTPUT]; then
    echo "Where is output name dude? Exiting" 1>&2
    exit
fi

DEVICE=${2:-"0"}

./AudioRecorder.py -v0 --device=$DEVICE $OUTPUT.mp3
