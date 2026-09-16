"""Helpers for the AICON lab notebooks.

The AICON code itself is installed unchanged from https://github.com/tu-rbo/aicon
(see binder/Dockerfile). This module only wraps it for use in notebooks:

- Blocksworld: run the synchronous experiment, record every state change, draw the towers.
- Drawer demo: start/stop ``aicon.drawer_tutorial.run_demo`` as a background process
  that shows the MuJoCo viewer on the VNC desktop.
"""

import contextlib
import io
import os
import random
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

PROJECT_DIR = Path(os.environ.get("PROJECT_DIR", "/home/jovyan/libs/aicon"))


# ============================================================================
# Blocksworld
# ============================================================================

BLOCKSWORLD_SETUPS = ("3towers", "0towers")
BLOCKSWORLD_GOALS = ("StackAonB", "StackAonBonC", "SmartStackAonBonC", "UnstackAonB")


@dataclass
class BlocksworldResult:
    init_setup: str
    goal: str
    fulfilled: bool
    steps: int
    snapshots: list = field(default_factory=list)  # dicts: step, action, state
    log: str = ""

    def summary(self):
        status = "goal reached" if self.fulfilled else "goal NOT reached"
        print(f"{self.init_setup} / {self.goal}: {status} after {self.steps} steps, "
              f"{len(self.snapshots) - 1} state changes")
        for snap in self.snapshots[1:]:
            print(f"  step {snap['step']:3d}: {snap['action']}")


def describe_action(action):
    """Translate AICON's (2, N, N) action tensor into words."""
    import torch

    kind, top, bottom = (int(i) for i in torch.unravel_index(torch.argmax(torch.abs(action)), action.shape))
    if kind == 0:
        return f"put block {top} on block {bottom}"
    return f"take block {top} off block {bottom}"


def _goals_fulfilled(components):
    for comp in components.values():
        for goal in comp.goals.values():
            if goal.is_active:
                return False
    return True


def run_blocksworld(init_setup="3towers", goal="StackAonBonC", max_steps=200, seed=111, verbose=False):
    """Run AICON's synchronous blocksworld experiment and record every state change.

    Mirrors ``aicon.blocksworld_experiment.run_experiment_sync``. AICON prints a lot
    (full tensors); that output is kept in ``result.log`` unless ``verbose=True``.
    """
    import torch
    from aicon.blocksworld_experiment.experiment_specifications import get_building_functions_basic_blocks_world
    from aicon.middleware.python_sequential import build_components, run_component_sequence

    if init_setup not in BLOCKSWORLD_SETUPS:
        raise ValueError(f"init_setup must be one of {BLOCKSWORLD_SETUPS}")
    if goal not in BLOCKSWORLD_GOALS:
        raise ValueError(f"goal must be one of {BLOCKSWORLD_GOALS}")

    # Same settings as the __main__ block of run_experiment_sync.py
    torch.set_default_dtype(torch.float64)
    with contextlib.suppress(AttributeError):
        torch._dynamo.config.capture_func_transforms = True
    torch.use_deterministic_algorithms(True)
    torch.autograd.set_detect_anomaly(True)
    torch.random.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    buffer = io.StringIO()
    stdout = sys.stdout if verbose else buffer
    with contextlib.redirect_stdout(stdout):
        component_builders, _, _ = get_building_functions_basic_blocks_world(init_setup=init_setup, goal=goal)
        components = build_components(component_builders)
        sensor = components["BlocksBelowSensor"]
        snapshots = [dict(step=0, action="initial state", state=sensor.current_sim_state.clone())]

        step = 0
        for step in range(max_steps):
            if _goals_fulfilled(components):
                break
            components = run_component_sequence(components, torch.tensor(step * 0.01))
            action = components["BlockPuttingAction"].internal_action
            if action is not None:
                before = sensor.current_sim_state.clone()
                sensor.take_action(action)
                if not torch.equal(before, sensor.current_sim_state):
                    snapshots.append(dict(step=step, action=describe_action(action),
                                          state=sensor.current_sim_state.clone()))
        fulfilled = _goals_fulfilled(components)

    return BlocksworldResult(init_setup=init_setup, goal=goal, fulfilled=fulfilled, steps=step + 1,
                             snapshots=snapshots, log=buffer.getvalue())


def draw_blocks(state, ax=None, title=""):
    """Draw towers from a below-matrix: state[i, j] == 1 means block j is somewhere below block i."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 3.5))
    below = np.asarray(state.detach().cpu() if hasattr(state, "detach") else state) > 0.5
    n = below.shape[0]
    height = below.sum(axis=1)

    column = {}
    for x, block in enumerate(i for i in range(n) if height[i] == 0):
        column[block] = x
    for block in sorted(range(n), key=lambda i: height[i]):
        if height[block] == 0:
            continue
        supports = [j for j in range(n) if below[block, j] and height[j] == height[block] - 1]
        column[block] = column.get(supports[0], len(column)) if supports else len(column)

    colors = plt.get_cmap("tab10")
    for block in range(n):
        x, y = column[block], height[block]
        ax.add_patch(plt.Rectangle((x + 0.05, y + 0.05), 0.9, 0.9, color=colors(block % 10)))
        ax.text(x + 0.5, y + 0.5, str(block), ha="center", va="center", color="white",
                fontsize=12, fontweight="bold")

    width = max(column.values()) + 1 if column else 1
    ax.set_xlim(-0.2, width + 0.2)
    ax.set_ylim(0, max(int(height.max()) + 1, 4) + 0.2)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", linewidth=2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)
    return ax


def browse_blocksworld(result):
    """Slider over all recorded states of a blocksworld run."""
    import ipywidgets as widgets
    import matplotlib.pyplot as plt

    def show(index):
        snap = result.snapshots[index]
        label = snap["action"] if index == 0 else f"step {snap['step']}: {snap['action']}"
        _, ax = plt.subplots(figsize=(6, 3.5))
        draw_blocks(snap["state"], ax=ax, title=f"[{index}/{len(result.snapshots) - 1}] {label}")
        plt.show()

    slider = widgets.IntSlider(min=0, max=len(result.snapshots) - 1, value=0, description="Change",
                               continuous_update=False)
    play = widgets.Play(min=0, max=len(result.snapshots) - 1, interval=1200)
    widgets.jslink((play, "value"), (slider, "value"))
    out = widgets.interactive_output(show, {"index": slider})
    return widgets.VBox([widgets.HBox([play, slider]), out])


# ============================================================================
# Drawer demo on the VNC desktop
# ============================================================================

class DrawerDemo:
    """Runs ``python -m aicon.drawer_tutorial.run_demo`` in the background.

    The demo loops forever and opens an OpenCV window with the MuJoCo rendering,
    so it runs as a separate process on the VNC desktop display instead of
    blocking the notebook kernel.
    """

    LOG_FILE = Path("/tmp/aicon_drawer_demo.log")

    def __init__(self, display=None):
        self.display = display or os.environ.get("DISPLAY") or ":1"
        self.process = None
        self._status = None
        self._log_view = None

    # --- process control -----------------------------------------------------
    def display_available(self):
        if shutil.which("xdpyinfo"):
            result = subprocess.run(["xdpyinfo", "-display", self.display],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            return result.returncode == 0
        number = self.display.split(":")[-1].split(".")[0]
        return Path(f"/tmp/.X11-unix/X{number}").exists()

    @property
    def running(self):
        return self.process is not None and self.process.poll() is None

    def start(self):
        if self.running:
            return "The demo is already running."
        if not self.display_available():
            return (f"No desktop on display {self.display} yet. Open the desktop first "
                    "(Launcher > 'Open Desktop Panel'), wait until it is visible, then press Start again.")
        env = dict(os.environ)
        env["DISPLAY"] = self.display
        env.setdefault("MUJOCO_GL", "osmesa")
        env.setdefault("PYOPENGL_PLATFORM", "osmesa")
        env.setdefault("QT_X11_NO_MITSHM", "1")
        log = open(self.LOG_FILE, "w")
        self.process = subprocess.Popen(
            [sys.executable, "-u", "-m", "aicon.drawer_tutorial.run_demo"],
            stdout=log, stderr=subprocess.STDOUT, env=env,
            cwd=PROJECT_DIR if PROJECT_DIR.is_dir() else None,
            start_new_session=True,
        )
        log.close()
        return f"Started (pid {self.process.pid}). The window appears on the desktop after the scene loads."

    def stop(self):
        if not self.running:
            return "The demo is not running."
        pgid = os.getpgid(self.process.pid)
        os.killpg(pgid, signal.SIGTERM)
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(pgid, signal.SIGKILL)
            self.process.wait()
        return "Stopped."

    def log_tail(self, lines=25):
        if not self.LOG_FILE.exists():
            return ""
        return "\n".join(self.LOG_FILE.read_text(errors="replace").splitlines()[-lines:])

    # --- notebook UI ---------------------------------------------------------
    def _refresh(self, message=None):
        import html

        state = "running" if self.running else "stopped"
        if self.process is not None and not self.running:
            state += f" (exit code {self.process.returncode})"
        self._status.value = f"<b>Status:</b> {state}" + (f"<br>{html.escape(message)}" if message else "")
        self._log_view.value = (
            "<pre style='max-height:22em;overflow:auto;font-size:11px'>"
            + html.escape(self.log_tail()) + "</pre>"
        )

    def _follow(self):
        while self.running:
            self._refresh()
            time.sleep(2)
        self._refresh()

    def ui(self):
        import ipywidgets as widgets

        start = widgets.Button(description="Start", button_style="success", icon="play")
        stop = widgets.Button(description="Stop", button_style="danger", icon="stop")
        refresh = widgets.Button(description="Refresh log", icon="refresh")
        self._status = widgets.HTML()
        self._log_view = widgets.HTML()

        def on_start(_):
            message = self.start()
            self._refresh(message)
            if self.running:
                threading.Thread(target=self._follow, daemon=True).start()

        start.on_click(on_start)
        stop.on_click(lambda _: self._refresh(self.stop()))
        refresh.on_click(lambda _: self._refresh())
        self._refresh()
        return widgets.VBox([widgets.HBox([start, stop, refresh]), self._status, self._log_view])
