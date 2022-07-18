#!/bin/bash

source venv/bin/activate
export NEWRL_ENV=$1
python -m app.main
