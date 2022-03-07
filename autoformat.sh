#!/bin/bash
TARGET=$1

if [[ $# -eq 0 ]] ; then
    TARGET="."
fi

echo "=== autoflake ==="
autoflake -i -r --remove-unused-variables --exclude=venv $TARGET

echo "=== isort ==="
isort $TARGET

echo "=== black ==="
black $TARGET
