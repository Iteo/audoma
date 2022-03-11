#!/bin/bash
EXIT=0

echo "=== isort ==="
python3 -m isort -c --diff .
EXIT=$(($EXIT + $?))

echo "=== flake8 ==="
python3 -m flake8
EXIT=$(($EXIT + $?))

echo "=== black ==="
python3 -m black --diff --check .
EXIT=$(($EXIT + $?))

echo "EXIT value: ${EXIT}"

exit $EXIT
