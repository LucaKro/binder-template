# IJCAI Planning Tutorial — Virtual Research Lab

[![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/LucaKro/binder-template/ijcai_chapter04)

This branch configures the Virtual Research Lab (VRL) for the IJCAI planning tutorial. A
VRL is part of the Virtual Research Building (VRB — https://vrb.ease-crc.org/) developed
by the AICOR Institute for Artificial Intelligence (https://ai.uni-bremen.de/).

The lab ships the CRAM cognitive architecture
(https://github.com/cram2/cognitive_robot_abstract_machine) together with the ROS 2
packages its simulated plans need, so the tutorial can be worked through in the browser
without installing anything. Click the badge above to enter it.

## What is in the lab

| Path | Contents |
| --- | --- |
| `~/cognitive_robot_abstract_machine` | The CRAM monorepo, checked out on the tutorial branch and installed editable. **The tutorial notebooks live here.** |
| `~/repo` | This repository — RViz configs and the lab's own configuration. |
| `~/ros2_ws` | ROS 2 overlay workspace, sourced automatically. |

CRAM is installed into the system interpreter, the same one `rclpy` comes from, so
notebooks can import `coraplex`, `giskardpy` and `semantic_digital_twin` alongside ROS 2
without selecting a virtualenv.

## Running the example

The tutorial's reference plan is a PR2 that opens a fridge, takes out a milk, closes the
fridge and places the milk on the kitchen island. It runs fully simulated — CRAM's motion
stack (giskardpy) runs in-process, so there is no simulator or motion server to start.

Open a Virtual Desktop in the VRL first, then:

Start RViz to watch the world:

```bash
ros2 run rviz2 rviz2 -d ~/repo/config/kitchen_fridge.rviz
```

The lab visualizes through `semantic_digital_twin`'s `VizMarkerPublisher`, which publishes
a `MarkerArray` on `/semworld/viz_marker` and the world's TF tree. The config's fixed
frame is `iai_oven_area/world`, the root body of the kitchen.

Run the plan:

```bash
python ~/cognitive_robot_abstract_machine/coraplex/demos/coraplex_kitchen_fridge_demo/demo.py
```

The demo asserts where the milk ended up and that the fridge door is shut again, so it
exits non-zero if the plan did not achieve its goal. Documentation on CRAM is here:
https://cram2.github.io/cognitive_robot_abstract_machine/.

## Updating the tutorial content

The notebooks are authored in the CRAM monorepo, on
[`LucaKro/cognitive_robot_abstract_machine@ijcai_planning_tutorials`](https://github.com/LucaKro/cognitive_robot_abstract_machine/tree/ijcai_planning_tutorials).
The image pins that branch by commit, so publishing new content takes three steps:

1. Push the notebooks to `ijcai_planning_tutorials`.
2. Bump `ARG CRAM_COMMIT` in [`binder/Dockerfile`](binder/Dockerfile) to the new SHA.
3. Push this branch.

Step 3 is what actually rebuilds the lab: BinderHub keys its image cache on *this*
repository's commit, so a change in CRAM alone is invisible to it.

The CRAM checkout in the image is owned by the notebook user and stays a normal git
working tree, so it can also be edited live from the Web IDE — useful while writing a
chapter, but those edits live only in the running lab.

## Development

All the software installed in this VRL is listed in [`binder/Dockerfile`](binder/Dockerfile):
a minimal ROS 2 overlay (`cram_ros2_packages` for `json_msgs`, `iai_pr2` for the PR2
description and meshes, `iai_maps` for the kitchen) on top of
`intel4coro/jupyter-ros2:jazzy-py3.12`, plus CRAM itself.

To build a new VRL from a new repo use this website: https://binder.intel4coro.de/

### Run and build docker image locally (under repo directory)

First edit the docker-compose.yml to have `user: root`. This eases the interaction with
the command line when inside the lab.

- Build and run docker image:

  ```bash
  docker compose -f ./binder/docker-compose.yml up --build
  ```

- Open a web browser and go to http://localhost:8888/

- To stop and remove container:

  ```bash
  docker compose -f ./binder/docker-compose.yml down
  ```
