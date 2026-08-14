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
| `~/repo` | This repository — RViz config, VSCode config and `scripts/run_demo.sh`. |
| `~/ros2_ws` | ROS 2 overlay workspace, sourced automatically. |

CRAM is installed into the lab's conda interpreter, `/opt/conda/bin/python` — what
`python` resolves to in a terminal, what the notebook kernel runs, and what the Web IDE is
configured to use. It sees ROS 2 as well, so notebooks can import `coraplex`, `giskardpy`
and `semantic_digital_twin` alongside `rclpy` without selecting a virtualenv.

The Web IDE opens on the CRAM checkout and is preconfigured there: the interpreter above,
a **Kitchen fridge demo** launch configuration, and a `.vscode/ros.env` holding the ROS 2
environment (launch configurations do not inherit the shell's, unlike the integrated
terminal). Nothing needs to be selected by hand.

Do not run the tutorial with `/bin/python3`. That is Ubuntu's system Python: it has ROS 2
but not CRAM, and greets you with `ModuleNotFoundError: No module named 'coraplex'`.

## Running the example

The tutorial's reference plan is a PR2 that opens a fridge, takes out a milk, closes the
fridge and places the milk on the kitchen island. It runs fully simulated — CRAM's motion
stack (giskardpy) runs in-process, so there is no simulator or motion server to start.

Open a Virtual Desktop in the VRL first, then:

Start RViz to watch the world:

```bash
ros2 run rviz2 rviz2
```

It comes up with the tutorial's config, which is installed as RViz's default
(`~/.rviz2/default.rviz`). The lab visualizes through `semantic_digital_twin`'s
`VizMarkerPublisher`, which publishes a `MarkerArray` on `/semworld/viz_marker` and the
world's TF tree; the fixed frame is `iai_oven_area/world`, the root body of the kitchen. If
the view gets saved over, reload the shipped one with
`ros2 run rviz2 rviz2 -d ~/repo/config/kitchen_fridge.rviz`.

Run the plan, either from the Web IDE — *Run and Debug* → **Kitchen fridge demo**, or F5
with the demo file open — or from a terminal:

```bash
~/repo/scripts/run_demo.sh
```

The script sources the ROS 2 overlay and runs the demo with the right interpreter. The
equivalent by hand is
`python ~/cognitive_robot_abstract_machine/coraplex/demos/coraplex_kitchen_fridge_demo/demo.py`.
The second launch configuration, **Python: current file**, runs whatever file is open the
same way — useful for the tutorial's own scripts.

The demo asserts where the milk ended up and that the fridge door is shut again, so it
exits non-zero if the plan did not achieve its goal. Documentation on CRAM is here:
https://cram2.github.io/cognitive_robot_abstract_machine/.

## Troubleshooting

**`ModuleNotFoundError: No module named 'coraplex'`** — the file is being run with
`/bin/python3`. Use `python` (`/opt/conda/bin/python`) or `~/repo/scripts/run_demo.sh`. In
the Web IDE, check the interpreter in the status bar; it should be the conda one.

**A "Build Recommended" dialog appears** — click Cancel, never Build. Rebuilding
JupyterLab inside a running lab breaks the open page. The image removes the source
extension that used to trigger this dialog and disables the builder, so it should not
appear at all.

**The launch configuration does not appear, or errors on the `debugpy` type** — the Web
IDE's Python debugger extension is older than the configuration expects. Change
`"type": "debugpy"` to `"type": "python"` in
[`config/vscode-launch.json`](config/vscode-launch.json) and rebuild.

**`ChunkLoadError: Loading chunk … failed`** — reload the page. This happens when
JupyterLab's static bundle is rebuilt underneath an open tab, which invalidates the chunk
hashes the tab is still asking for.

## Updating the tutorial content

The notebooks are authored in the CRAM monorepo, on
[`LucaKro/cognitive_robot_abstract_machine@ijcai_planning_tutorials`](https://github.com/LucaKro/cognitive_robot_abstract_machine/tree/ijcai_planning_tutorials).
The image pins that branch by commit, so publishing new content takes three steps:

1. Push the notebooks to `ijcai_planning_tutorials`.
2. Repin this repository to the new tip:

   ```bash
   scripts/update_cram_pin.sh
   ```

   It reads the repository and branch out of `binder/Dockerfile`, resolves the branch tip
   with `git ls-remote`, rewrites `ARG CRAM_COMMIT` and prints a compare link for what
   moved. `--check` reports without touching anything.
3. `git commit -am '…' && git push`.

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
