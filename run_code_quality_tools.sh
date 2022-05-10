#!/bin/bash

echo -e "Activate virtual environment\n"
source ./venv/bin/activate

echo -e "Running black\n"
python -m black app/ tests/
echo -e "Running isort\n"
python -m isort app/ tests/
echo -e "Running pylint\n"
python -m pylint app/ tests/
echo -e "Running tests\n"
viktor-cli test

echo -e "Deactivate virtual environment\n"
deactivate
