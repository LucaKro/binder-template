# Dockerfile of the base image: https://github.com/IntEL4CoRo/jupyter-ros2/blob/main/Dockerfile
FROM intel4coro/jupyter-ros2:jazzy-py3.12

USER root
#============= Install extra software packages =============#
# Install python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
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
ARG CRAM_COMMIT=5c5e3eee470e2dc94c15601951a6427400536a51
ENV CRAM_DIR=${HOME}/cognitive_robot_abstract_machine

RUN pip install poetry && \
    poetry config virtualenvs.create false

# Installing without a virtualenv puts CRAM into the same interpreter rclpy lives in.
RUN set -ex && \
    git clone -b ${CRAM_BRANCH} ${CRAM_REPO} ${CRAM_DIR} && \
    cd ${CRAM_DIR} && git checkout ${CRAM_COMMIT} && \
    poetry install && \
    pip install "setuptools<81" && \
    git config --global --add safe.directory ${CRAM_DIR} && \
    chown -R ${NB_USER}:users ${CRAM_DIR}

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

# Set JupyterLab default directory
WORKDIR ${HOME}

# Set VSCODE default directory
ENV CODE_WORKING_DIRECTORY=${HOME}

# The entrypoint of the docker image
COPY binder/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
