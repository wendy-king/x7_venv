#!/bin/bash
TOOLS=`dirname $0`
VENV=$TOOLS/../.steer-venv
source $VENV/bin/activate && $@
