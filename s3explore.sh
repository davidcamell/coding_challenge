#!/bin/bash
export S3X_PATH=${PWD}
export PYTHONPATH=$PYTHONPATH:$S3X_PATH/src
source env/env_s3explore/bin/activate
python3 src/main.py "$@"