#!/bin/bash
NEO4J_APP="/Applications/Neo4j Desktop.app"
PYTHON="/usr/local/bin/python3"
SCRIPT="db/populate_db.py"
open -a "$NEO4J_APP"
sleep 30
$PYTHON "$SCRIPT"
wait
sudo shutdown -h now
