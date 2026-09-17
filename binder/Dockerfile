# Dockerfile for the VRB lab "aicon-vrb-lab"
#
# Base image (ROS 2 + JupyterLab + VSCode + VNC desktop):
#   https://github.com/IntEL4CoRo/jupyter-ros2
# The jazzy-py3.12 tag is used for its Python 3.12 (matches AICON) and the VNC
# desktop that shows the MuJoCo viewer. ROS itself is not used by this lab.
#
# Build-cache rule: steps that are slow and rarely change go at the TOP,
# steps that use this repository's files go at the BOTTOM (after COPY).
FROM intel4coro/jupyter-ros2:jazzy-py3.12

USER root
ENV DEBIAN_FRONTEND=noninteractive

#================= SYSTEM PACKAGES (apt) =====================================#
# libosmesa6 / libgl1 / libegl1 / libglfw3: OpenGL for MuJoCo rendering
# nodejs / npm: build the desktop panel JupyterLab extension
RUN apt update && apt install -y --no-install-recommends \
        libosmesa6 \
        libgl1 \
        libegl1 \
        libglfw3 \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# Binder has no GPU: render MuJoCo in software. robosuite would otherwise force EGL.
ENV MUJOCO_GL=osmesa
ENV PYOPENGL_PLATFORM=osmesa

#================= EXTERNAL REPOSITORIES ======================================#
# Pinned commits for a reproducible lab. HTTPS URLs only.
ENV LIBS_DIR=/home/${NB_USER}/libs

# AICON (tu-rbo/aicon, master)
ARG AICON_COMMIT=6865ef4051dbea090f4872e56a828d8821ec6593
ENV PROJECT_DIR=${LIBS_DIR}/aicon
RUN mkdir -p ${PROJECT_DIR} && cd ${PROJECT_DIR} && \
    git init -q && \
    git remote add origin https://github.com/tu-rbo/aicon.git && \
    git fetch -q --depth=1 origin ${AICON_COMMIT} && \
    git checkout -q FETCH_HEAD

# run_demo.py imports SpaceMouse, which robosuite only exports when the `hid`
# module (3D mouse driver) is installed. It is unused, so drop it from the import.
# grep fails the build if the line changes after an AICON_COMMIT update.
RUN cd ${PROJECT_DIR}/src/aicon/drawer_tutorial && \
    grep -q '^from robosuite.devices import Keyboard, SpaceMouse$' run_demo.py && \
    sed -i 's/^from robosuite.devices import Keyboard, SpaceMouse$/from robosuite.devices import Keyboard/' run_demo.py

# robosuite-task-zoo (provides the cabinet model used by the drawer demo)
ARG TASK_ZOO_COMMIT=74eab7f88214c21ca1ae8617c2b2f8d19718a9ed
RUN mkdir -p ${LIBS_DIR}/robosuite-task-zoo && cd ${LIBS_DIR}/robosuite-task-zoo && \
    git init -q && \
    git remote add origin https://github.com/ARISE-Initiative/robosuite-task-zoo.git && \
    git fetch -q --depth=1 origin ${TASK_ZOO_COMMIT} && \
    git checkout -q FETCH_HEAD

#================= PYTHON PACKAGES (pip) ======================================#
# CPU-only PyTorch first, so AICON's torch pin does not pull ~2.5 GB of CUDA libraries.
RUN python3 -m pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch==2.4.0 torchvision==0.19.0

# AICON with the dependencies from its pyproject.toml
RUN python3 -m pip install --no-cache-dir -e ${PROJECT_DIR}

# robosuite, MuJoCo and notebook helpers
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# setup.py of robosuite-task-zoo requires mujoco-py, which its code never imports
RUN python3 -m pip install --no-cache-dir --no-deps -e ${LIBS_DIR}/robosuite-task-zoo

#================= DESKTOP PANEL EXTENSION ====================================#
# Small JupyterLab extension that opens the VNC desktop as a docked tab.
# Copied on its own so notebook edits do not trigger a rebuild of JupyterLab.
COPY binder/desktop-widget /opt/desktop-widget
RUN cd /opt/desktop-widget && \
    npm install && \
    npm run build && \
    jupyter labextension install . --no-build && \
    jupyter lab build --minimize=False && \
    npm cache clean --force

#================= COPY THIS REPOSITORY INTO THE IMAGE ========================#
# Everything below this line re-runs on every push.
ENV REPO_DIR=/home/repo
RUN mkdir -p ${REPO_DIR}
COPY . ${REPO_DIR}/
RUN git config --global --add safe.directory ${REPO_DIR}

# JupyterLab and VSCode start in the repository
WORKDIR ${REPO_DIR}
ENV CODE_WORKING_DIRECTORY=${REPO_DIR}

#================= ENTRYPOINT =================================================#
COPY binder/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
