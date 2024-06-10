#!/bin/bash

DEVICE=${1:-"0"}

./Camera.py -v1 --device=$DEVICE
