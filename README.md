# AICON: Active InterCONnect Lab

[![Binder](https://binder.intel4coro.de/badge_logo.svg)](https://binder.intel4coro.de/v2/gh/LucaKro/binder-template/aicon_vrb?urlpath=lab/tree/notebooks/welcome.ipynb)

Try [AICON](https://github.com/tu-rbo/aicon) in your browser. AICON is a framework for robotic systems that estimate states and select actions by gradient descent through dynamically interconnected, differentiable components, solving sequential tasks without an explicit plan
(Mengers & Brock, *No Plan but Everything Under Control*, ICRA 2025, [project website](https://www.tu.berlin/robotics/papers/noplan)).
The lab contains two demos: a blocksworld stacking task that runs inside a notebook, and a simulated Panda robot opening a drawer (robosuite/MuJoCo), shown on a remote desktop next to the notebook.

This lab is part of the [EASE Virtual Research Building (VRB)](https://vrb.ease-crc.org/).
It packages [AICON](https://github.com/tu-rbo/aicon) so it can be tried in the browser without installing anything.

## Launch

| Interface | Link |
|-----------|------|
| JupyterLab (opens `notebooks/welcome.ipynb`) | https://binder.intel4coro.de/v2/gh/LucaKro/binder-template/aicon_vrb?urlpath=lab/tree/notebooks/welcome.ipynb |
| Drawer demo with the desktop panel already open | https://binder.intel4coro.de/v2/gh/LucaKro/binder-template/aicon_vrb?urlpath=lab/tree/notebooks/drawer_demo.ipynb%3FautoOpenDesktop%3D1 |
| VSCode | https://binder.intel4coro.de/v2/gh/LucaKro/binder-template/aicon_vrb?urlpath=vscode |

The first launch after a push builds the Docker image and can take a long time. Later launches reuse the image.

To freeze the lab to a specific version, replace `aicon_vrb` in the URL with a tag or a commit hash.

## What is inside

- `notebooks/welcome.ipynb` – start here: overview and environment check
- `notebooks/blocksworld.ipynb` – blocksworld experiment with step-by-step plots
- `notebooks/drawer_demo.ipynb` – simulated drawer opening on the remote desktop
- `notebooks/lab_utils.py` – notebook helpers (the AICON code itself is used unchanged)
- `binder/Dockerfile` – how the image is built: base image, AICON and robosuite-task-zoo at pinned commits, CPU-only PyTorch, robosuite/MuJoCo, desktop panel extension
- `binder/desktop-widget/` – JupyterLab extension that opens the remote desktop as a panel ("Open Desktop Panel" in the launcher and command palette; `?autoOpenDesktop=1` in the URL opens it at startup)
- `binder/entrypoint.sh` – what runs before JupyterLab starts
- `requirements.txt` – Python packages installed in addition to AICON's own dependencies
- `binder/docker-compose.yml` – run the lab locally

To update AICON, change `AICON_COMMIT` in `binder/Dockerfile`.

## Run locally

Requires Docker and Docker Compose on Linux.

```bash
docker compose -f binder/docker-compose.yml up --build
# open http://localhost:8888/lab/tree/notebooks/welcome.ipynb
docker compose -f binder/docker-compose.yml down
```

The repository is mounted into the container, so notebook and code edits are visible immediately.
Files created inside the container belong to root; fix ownership with `sudo chown -R $USER:$USER .` if needed.

## Credits

AICON is developed by Vito Mengers and Oliver Brock at the [Robotics and Biology Laboratory, TU Berlin](https://www.tu.berlin/robotics), MIT License.
If you use it, please cite:

```bibtex
@inproceedings{mengers2025noplan,
  author={Mengers, Vito and Brock, Oliver},
  booktitle={IEEE International Conference on Robotics and Automation (ICRA)},
  title={No Plan but Everything Under Control: Robustly Solving Sequential Tasks with Dynamically Composed Gradient Descent},
  year={2025}
}
```

Lab created with the `setup-vrb-lab` skill from [aicor-vrb/binder-template](https://github.com/aicor-vrb/binder-template).
