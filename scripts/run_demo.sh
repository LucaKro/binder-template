#!/bin/bash
# Run the kitchen fridge demo with the ROS 2 overlay sourced and the interpreter CRAM
# is installed in. /bin/python3 has ROS 2 but not CRAM, which is the usual way this
# goes wrong.
set -e

source /opt/ros/jazzy/setup.bash
source "${OVERLAY_WS:-$HOME/ros2_ws}/install/setup.bash"

exec /opt/conda/bin/python \
  "$HOME/cognitive_robot_abstract_machine/coraplex/demos/coraplex_kitchen_fridge_demo/demo.py" "$@"
