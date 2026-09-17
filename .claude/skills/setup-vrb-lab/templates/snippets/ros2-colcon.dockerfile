# --- Build a ROS 2 workspace with colcon ----------------------------------------
# Variant A (cached): project cloned in EXTERNAL REPOSITORIES into a workspace
# outside the repo. Put this block right after the clone, before COPY.
ENV ROS2_WS=/home/${NB_USER}/ros2_ws
RUN mkdir -p ${ROS2_WS}/src && \
    git clone --depth=1 --branch __BRANCH__ __PROJECT_URL__ ${ROS2_WS}/src/__PROJECT_NAME__ && \
    cd ${ROS2_WS} && \
    . ${ROS_PATH}/setup.sh && \
    (rosdep init >/dev/null 2>&1 || true) && rosdep update && \
    apt update && rosdep install --from-paths src --ignore-src -y && \
    rm -rf /var/lib/apt/lists/* && \
    colcon build --symlink-install && \
    rm -rf build log
# Then add to binder/entrypoint.sh's workspace loop: "/home/jovyan/ros2_ws/install/setup.bash"

# Variant B (rebuilds on every push): project COPIED into the repo under ros2_ws/src.
# Put this block in PROJECT BUILD STEPS (after COPY). Matches the entrypoint default path.
# RUN cd ${REPO_DIR}/ros2_ws && \
#     . ${ROS_PATH}/setup.sh && \
#     (rosdep init >/dev/null 2>&1 || true) && rosdep update && \
#     apt update && rosdep install --from-paths src --ignore-src -y && \
#     rm -rf /var/lib/apt/lists/* && \
#     colcon build --symlink-install
