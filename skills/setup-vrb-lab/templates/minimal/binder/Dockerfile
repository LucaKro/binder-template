# Dockerfile for the VRB lab "__LAB_NAME__"
#
# Base image (ROS 2 + JupyterLab + VSCode + VNC desktop):
#   https://github.com/IntEL4CoRo/jupyter-ros2
# Other tags / ROS versions: see skills/setup-vrb-lab/reference/base-images.md
#
# Build-cache rule: steps that are slow and rarely change go at the TOP,
# steps that use this repository's files go at the BOTTOM (after COPY).
FROM __BASE_IMAGE__

USER root
ENV DEBIAN_FRONTEND=noninteractive

#================= SYSTEM PACKAGES (apt) =====================================#
# Keep `apt update` and `apt install` in the same RUN.
# RUN apt update && apt install -y --no-install-recommends \
#         ffmpeg \
#     && rm -rf /var/lib/apt/lists/*

#================= EXTERNAL REPOSITORIES ======================================#
# Clone projects, model zoos, ROS packages here so they are cached between
# pushes. HTTPS URLs only (SSH does not work on Binder).
# RUN git clone --depth=1 --branch main https://github.com/<org>/<repo>.git /home/${NB_USER}/libs/<repo>

#================= PYTHON PACKAGES (pip) ======================================#
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

#================= COPY THIS REPOSITORY INTO THE IMAGE ========================#
# Everything below this line re-runs on every push.
ENV REPO_DIR=/home/repo
RUN mkdir -p ${REPO_DIR}
COPY . ${REPO_DIR}/
RUN git config --global --add safe.directory ${REPO_DIR}

# JupyterLab and VSCode start in the repository
WORKDIR ${REPO_DIR}
ENV CODE_WORKING_DIRECTORY=${REPO_DIR}

#================= PROJECT BUILD STEPS ========================================#
# Steps that need the repository contents: pip install -e, colcon build, ...
# See skills/setup-vrb-lab/templates/snippets/ for ready-made blocks.


#================= ENTRYPOINT =================================================#
COPY binder/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
