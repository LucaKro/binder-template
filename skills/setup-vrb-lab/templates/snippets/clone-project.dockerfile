# --- Clone the project from GitHub (put in the EXTERNAL REPOSITORIES section) ---
# Placed BEFORE `COPY . ${REPO_DIR}/` so Docker caches it between pushes.
# Pin __BRANCH__ to a tag or commit for a reproducible lab. HTTPS URL only.
ENV PROJECT_DIR=/home/${NB_USER}/libs/__PROJECT_NAME__
RUN git clone --depth=1 --branch __BRANCH__ __PROJECT_URL__ ${PROJECT_DIR}
# To pin an exact commit instead (drop --depth=1 and --branch):
# RUN git clone __PROJECT_URL__ ${PROJECT_DIR} && git -C ${PROJECT_DIR} checkout __COMMIT__
