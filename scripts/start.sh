#!/bin/bash

source venv/bin/activate
export NEWRL_ENV=$1
python -m app.main $2 $3 $4 $5 $6 $7
