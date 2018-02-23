#!/bin/bash

source deter.conf

cd $WEBDASH_CLONE/Dash2/distributed_github/
python dash_worker.py 127.0.0.1:2181 $1.
echo node $1 started

