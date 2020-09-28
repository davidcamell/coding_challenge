#!/bin/bash

S3X_PATH=${PWD}
DATA_DIR=$S3X_PATH/data
CRED_FILE=$DATA_DIR/.cred.json
CRED_EXAMPLE=$S3X_PATH/installation_support/cred_EXAMPLE.json

python3 -m venv env/env_s3explore
source env/env_s3explore/bin/activate

export S3X_PATH=${PWD}
export PYTHONPATH=$PYTHONPATH:$S3X_PATH/src

pip install -r installation_support/requirements.txt

if ! test -d "$DATA_DIR"; then
  mkdir "$DATA_DIR"
  echo "Created $DATA_DIR"
fi

RED='\033[0;31m'  # ANSI Red for printing critical WARNING
GREEN='\033[0;32m'  # ANSI Green for printing Important reminder
NC='\033[0m'  # ANSI No Color for ending highlighted output

if test -f "$CRED_FILE"; then
    echo "Credential file '$CRED_FILE' already exists."
else
    if test -f "$CRED_EXAMPLE"; then
        cp "$CRED_EXAMPLE" "$CRED_FILE"
        echo "New credential file '$CRED_FILE' created from default example '$CRED_EXAMPLE'."
    else
        printf "${RED}\nWARNING:\nNeither '%s' OR '%s' exist.\n" "$CRED_FILE" "$CRED_EXAMPLE"
        printf "Check to make sure install contents are complete.\n${NC}"
    fi
fi
printf "${GREEN}\nRefer to README for credential managament before running program.\n${NC}"

