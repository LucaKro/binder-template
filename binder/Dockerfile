# Dockerfile of the base image: https://github.com/IntEL4CoRo/jupyter-ros2/blob/main/Dockerfile
FROM intel4coro/jupyter-ros2:jazzy-py3.12

USER root

# Set by the jupyter docker-stacks base; restated so the interpreter this image
# installs into is explicit rather than whatever PATH happens to resolve to.
ENV CONDA_DIR=${CONDA_DIR:-/opt/conda}

#============= Install extra software packages =============#
# Install python packages
COPY requirements.txt /tmp/requirements.txt
RUN ${CONDA_DIR}/bin/pip install -r /tmp/requirements.txt
#===========================================================#

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------
RUN apt update && apt install -y --no-install-recommends \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro \
    ros-jazzy-rclpy-message-converter \
    ros-jazzy-rosidl-default-generators \
    python3-colcon-common-extensions \
    python3-vcstool \
    graphviz graphviz-dev \
    default-jre \
    git-lfs && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# ROS 2 overlay workspace
#
# Only the packages the tutorial resolves at runtime:
#   cram_ros2_packages -> json_msgs, imported by giskardpy.middleware.ros2
#   iai_pr2            -> iai_pr2_description, the PR2 xacro and its meshes
#   iai_maps           -> iai_kitchen, referenced by kitchen-small.urdf
#
# iai_pr2_bringup, iai_pr2_controller_configuration and iai_pr2_sim are still ROS 1
# catkin packages with no ament build type, so colcon cannot build them and they
# are dropped. Only iai_pr2_description is needed anyway.
# ------------------------------------------------------------
ENV OVERLAY_WS=${HOME}/ros2_ws

RUN set -ex && \
    mkdir -p ${OVERLAY_WS}/src && cd ${OVERLAY_WS}/src && \
    git clone --depth 1 -b main https://github.com/cram2/cram_ros2_packages.git && \
    git clone --depth 1 -b ros-jazzy-main https://github.com/code-iai/iai_pr2.git && \
    git clone --depth 1 -b ros-jazzy https://github.com/code-iai/iai_maps.git && \
    rm -rf iai_pr2/iai_pr2_bringup iai_pr2/iai_pr2_controller_configuration iai_pr2/iai_pr2_sim && \
    cd ${OVERLAY_WS} && \
    /bin/bash -lc "source /opt/ros/jazzy/setup.bash && colcon build --merge-install"

# ------------------------------------------------------------
# CRAM
#
# The tutorial notebooks live in this checkout, so it is owned by the notebook
# user and stays writable. Bump CRAM_COMMIT to pull in new tutorial content.
# ------------------------------------------------------------
ARG CRAM_REPO=https://github.com/LucaKro/cognitive_robot_abstract_machine.git
ARG CRAM_BRANCH=ijcai_planning_tutorials
ARG CRAM_COMMIT=8ebb62459266f21f19b54f17be3a2786e804fcd1
ENV CRAM_DIR=${HOME}/cognitive_robot_abstract_machine

RUN ${CONDA_DIR}/bin/pip install poetry && \
    ${CONDA_DIR}/bin/poetry config virtualenvs.create false

# Installing without a virtualenv puts CRAM into the conda interpreter, which is the
# one JupyterLab's kernel and the desktop's `python` use, and which sees ROS 2 through
# PYTHONPATH once /opt/ros/jazzy is sourced. /bin/python3 is a different interpreter
# and does not get CRAM.
RUN set -ex && \
    git clone -b ${CRAM_BRANCH} ${CRAM_REPO} ${CRAM_DIR} && \
    cd ${CRAM_DIR} && git checkout ${CRAM_COMMIT} && \
    ${CONDA_DIR}/bin/poetry install && \
    ${CONDA_DIR}/bin/pip install "setuptools<81" && \
    git config --global --add safe.directory ${CRAM_DIR} && \
    chown -R ${NB_USER}:users ${CRAM_DIR}

# Fail the build here rather than in a learner's face if CRAM or the overlay ended up
# somewhere the notebooks cannot import from.
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && \
    source ${OVERLAY_WS}/install/setup.bash && \
    ${CONDA_DIR}/bin/python -c 'import rclpy, json_msgs.action, coraplex, giskardpy, semantic_digital_twin; print(\"imports ok\")'"

# dash, which CRAM pulls in for plotting, ships a *source* labextension. JupyterLab
# offers to rebuild itself for those on every start, and rebuilding rewrites the static
# bundle under the open page, so every lazily loaded chunk (terminals among them) 404s
# afterwards. Drop the source extension and the builder plugin; the prebuilt extensions
# in share/jupyter/labextensions (plotly, open3d, sidecar, widgets) are unaffected.
RUN rm -f ${CONDA_DIR}/share/jupyter/lab/extensions/*.tgz && \
    ${CONDA_DIR}/bin/jupyter labextension disable "@jupyterlab/apputils-extension:builder" --level=sys_prefix

# The entrypoint covers the JupyterLab process tree, .bashrc covers terminals
# opened in the Web IDE and on the desktop.
RUN echo "source ${OVERLAY_WS}/install/setup.bash" >> ${HOME}/.bashrc

USER root
# Copy content to the image
ENV REPO_DIR=/home/repo
RUN mkdir -p ${REPO_DIR}
COPY . ${REPO_DIR}/
RUN git config --global --add safe.directory ${REPO_DIR} && \
    ln -sfn ${REPO_DIR} ${HOME}/repo && \
    chown -h ${NB_USER}:users ${HOME}/repo

# rviz2 started without -d loads ~/.rviz2/default.rviz, so the tutorial's config is
# what a bare `ros2 run rviz2 rviz2` comes up with. The copy stays writable; the one in
# the repo remains the source of truth.
RUN mkdir -p ${HOME}/.rviz2 && \
    cp ${REPO_DIR}/config/kitchen_fridge.rviz ${HOME}/.rviz2/default.rviz && \
    chown -R ${NB_USER}:users ${HOME}/.rviz2

# Web IDE setup, in the CRAM checkout because that is the folder VSCode opens:
# the conda interpreter CRAM is installed in, and a launch configuration for the
# demo. A launch configuration does not inherit the shell's environment the way the
# integrated terminal does, so the ROS 2 environment is dumped to an env file the
# configurations point at -- rclpy needs PYTHONPATH and LD_LIBRARY_PATH from it, and
# semantic_digital_twin resolves package:// through ament_index_python, which reads
# AMENT_PREFIX_PATH. CRAM's own .gitignore covers .vscode/, so this leaves its git
# status clean.
RUN /bin/bash -c 'mkdir -p ${CRAM_DIR}/.vscode && \
    cp ${REPO_DIR}/config/vscode-settings.json ${CRAM_DIR}/.vscode/settings.json && \
    cp ${REPO_DIR}/config/vscode-launch.json ${CRAM_DIR}/.vscode/launch.json && \
    source /opt/ros/jazzy/setup.bash && \
    source ${OVERLAY_WS}/install/setup.bash && \
    env | grep -E "^(AMENT_PREFIX_PATH|CMAKE_PREFIX_PATH|COLCON_PREFIX_PATH|LD_LIBRARY_PATH|PYTHONPATH|RMW_IMPLEMENTATION|ROS_[A-Z_]+)=" \
      > ${CRAM_DIR}/.vscode/ros.env && \
    chown -R ${NB_USER}:users ${CRAM_DIR}/.vscode'

# Set JupyterLab default directory
WORKDIR ${HOME}

# Set VSCODE default directory: the tutorial content lives in the CRAM checkout
ENV CODE_WORKING_DIRECTORY=${CRAM_DIR}

# The entrypoint of the docker image
COPY binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
