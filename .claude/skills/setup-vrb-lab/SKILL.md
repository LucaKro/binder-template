---
name: setup-vrb-lab
description: Turn an existing research project (local folder or GitHub repo) into a new Virtual Research Lab for the EASE Virtual Research Building (VRB) that runs on BinderHub. Guides a first-time lab author step by step, asks before every decision that is not obvious, and never touches git or GitHub without explicit consent. Use when someone wants to create, set up, or integrate a project into a VRB lab / Binder lab.
---

# Set up a new Virtual Research Lab (VRB)

You are helping someone who has probably never built a VRB lab before. Your job is to
turn **their project** into a **public GitHub repository** that BinderHub
(`https://binder.intel4coro.de`) can build into a Docker image and launch as JupyterLab.

Work interactively. Explain what each step does in one or two sentences before doing it.
Prefer asking one focused question over guessing.

## Hard rules

1. **Never run git or GitHub commands without being told to.** No `git init`, `git add`,
   `git commit`, `git push`, `gh repo create`, no creating branches, tags, or repos.
   Always show the exact command, explain what it does, and wait for a clear "yes".
   Approval for one command does not carry over to the next one.
2. **Always propose a local Docker build test before pushing.** Online builds on Binder
   are slow (often 10 to 40 minutes). Local iteration finds small mistakes in minutes.
3. **Do not modify the user's original project** unless they ask. Work in a new lab directory.
4. **When the project analysis is ambiguous, ask.** Do not invent dependencies, ROS
   distributions, or entry points.
5. If any file you generate contains a placeholder (`__LIKE_THIS__`), fill it in or
   ask for the value. Never leave placeholders behind.

## Files that belong to this skill

All paths are relative to the directory that contains this `SKILL.md`:

| Path | Purpose |
|------|---------|
| `templates/minimal/` | Complete lean lab skeleton (Dockerfile, entrypoint, compose, README, notebook) |
| `templates/snippets/*.dockerfile` | Dockerfile blocks to splice in: clone project, pip install, colcon (ROS 2), catkin (ROS 1), ROS 1 base image |
| `reference/project-analysis.md` | How to detect what kind of project the user has and what it needs |
| `reference/base-images.md` | Available base images and which ROS versions they support |
| `reference/troubleshooting.md` | Build and runtime problems with fixes; the checklist to run before pushing |

The **template repository itself** (the repository that contains this skill, three directories
above this file) is the "CRAM preinstalled" flavor. If you are not running inside a clone
of it, it is at `https://github.com/aicor-vrb/binder-template`. Ask before cloning it.

## Workflow

### Step 0: Check the tools

Run these and report what is available. Missing tools are not blockers; they change
what you can offer later.

```bash
git --version
docker --version && docker compose version && docker info >/dev/null && echo "docker daemon reachable"
gh --version && gh auth status
```

Docker missing means no local build test (say so clearly and recommend installing it).
`docker info` failing with "permission denied ... docker.sock" means the user is not in the
`docker` group: suggest `sudo usermod -aG docker $USER` followed by a re-login (do not run
it yourself). `gh` missing means GitHub steps are done in the browser instead of the CLI.

### Step 1: Find out what should be integrated

If the user has not already said which project to integrate, ask:

> Which project should become the lab? Give me a local directory path or a GitHub URL.

Then determine:

- **Local directory** → confirm it exists and list its top level.
- **GitHub URL** → normalize to HTTPS (`https://github.com/<org>/<repo>.git`). SSH URLs do
  not work inside Binder builds. Ask which branch, tag, or commit to use; default `main`.
  Clone it read-only into a temporary directory to analyze it (this is not a git decision
  about *their* repo, but tell them you are doing it).
- Neither → ask again; do not proceed without a project.

### Step 2: Analyze the project

Follow `reference/project-analysis.md`. Produce a short summary for the user in plain words:

- What kind of project it is (Python package, ROS 2 workspace, ROS 1 workspace, notebooks only, mixed, unknown)
- Which ROS distribution it appears to need, if any, and how confident you are
- Python dependencies found (and where: `requirements.txt`, `pyproject.toml`, `setup.py`, `environment.yml`)
- System (apt) dependencies you can see (README install sections, `package.xml`, Dockerfiles)
- Notebooks found, and a guess at the best "open this first" notebook
- Anything you could not figure out

Ask the user to confirm or correct this summary before continuing. Concretely ask about
every "unknown" item.

### Step 3: Decisions (ask, do not assume)

Ask these one at a time. Recommend an option when the analysis supports it, but let the user choose.

1. **Flavor**
   - *Minimal*: lean image built from `templates/minimal/`. Fast builds. Recommended for
     most projects.
   - *CRAM preinstalled*: copy of the template repository including the PyCRAM /
     cognitive_robot_abstract_machine stack, IAI robot descriptions, colcon workspace,
     demo notebook UI and RViz autostart. Very long build (well over an hour on Binder).
     Only sensible when the project builds on PyCRAM or the IAI robots.
2. **ROS version** (see `reference/base-images.md`)
   - None, ROS 2 Jazzy (default base image), ROS 2 Humble, ROS 1 Noetic, or another
     distribution. Recommend what the analysis found. If the project needs a
     distribution that no ready-made image covers, explain the "other base image" path
     (install JupyterLab yourself, expose port 8888) and its trade-offs (no VSCode, no
     VNC desktop unless they add it).
3. **How to bring the project into the lab**
   | Mode | When to recommend | What it means |
   |------|-------------------|---------------|
   | Copy | Project is a local directory, or the user wants the lab to be self-contained | Files are copied into the lab repo and land in the image via `COPY . /home/repo/` |
   | Clone in Dockerfile | Project is on GitHub and evolves independently | `RUN git clone` placed *before* the `COPY` line so Docker caches it; pin a branch/tag/commit |
   | Git submodule | User wants version tracking of the project inside the lab repo | `git submodule add <https url>`; remind them: HTTPS only, and the lab README must mention `--recurse-submodules` |
   Default: local → Copy, GitHub URL → Clone in Dockerfile.
4. **Lab name** (also becomes the directory name and, later, the repo name). Suggest
   `<project>-vrb-lab` or similar; lowercase, hyphens.
5. **Where to create the lab directory** on disk. Suggest a sibling of the project.
6. **Which notebook opens at launch.** Offer the guess from Step 2, or create a
   `notebooks/welcome.ipynb` from the template.
7. **Extras**: GPU section in compose (only for local use), RViz autostart, desktop panel.
   Default all off for Minimal.

Summarize all decisions in a table and get one final confirmation.

### Step 4: Generate the lab

**Minimal flavor**

1. Copy `templates/minimal/` into the new lab directory (including the dotfile `.gitignore`).
2. Fill placeholders in every copied file:
   `__LAB_NAME__`, `__LAB_TITLE__`, `__LAB_DESCRIPTION__`, `__GITHUB_USER__`, `__REPO__`,
   `__BRANCH__`, `__DEFAULT_NOTEBOOK__`, `__BASE_IMAGE__`, `__PROJECT_NAME__`,
   `__PROJECT_URL__`. If GitHub owner/repo are not decided yet, ask now; they are needed
   for the launch links in the README.
3. Bring in the project according to the chosen mode:
   - Copy: `cp -r` the project into `<lab>/<project-name>/` (exclude `.git`, `__pycache__`,
     virtualenvs, large data unless the user wants it). Tell the user what was excluded.
   - Clone: splice `templates/snippets/clone-project.dockerfile` into the Dockerfile at the
     marked `EXTERNAL REPOSITORIES` section.
   - Submodule: show the `git submodule add` command and wait for consent (Hard rule 1).
4. Add install/build steps from `templates/snippets/` at the marked `PROJECT BUILD STEPS`
   section:
   - Python package → `python-package.dockerfile`
   - ROS 2 package(s) → `ros2-colcon.dockerfile`
   - ROS 1 package(s) → `ros1-catkin.dockerfile` (and `ros1-noetic-base.dockerfile` as the
     `FROM` block if ROS 1 was chosen)
   - Plain requirements → append to `requirements.txt`
5. Add apt packages found in Step 2 to the `SYSTEM PACKAGES` section.
6. Review the Dockerfile for cache order: apt and clones near the top, `COPY . ${REPO_DIR}/`
   as late as possible, only steps that need the repo contents after it.

**CRAM preinstalled flavor**

1. Copy the entire template repository (all files except `.git`, `.idea`, and the
   `.claude/` directory unless the user wants to keep the skill) into the lab directory.
2. Keep the existing Dockerfile blocks. Insert the project clone before the
   `COPY . ${REPO_DIR}/` line and the project build steps after it, using the same snippets.
3. Point out the demo-specific parts they may want to change or remove later:
   `notebooks/demo.ipynb` and `notebooks/demo_ui.py` (the robot/action/environment UI),
   the `update_cognitive_architecture` function in `binder/entrypoint.sh` (pulls CRAM on
   every start), `default.rviz`, the license and author cell in the demo notebook.
4. Rewrite `README.md` launch links to the new owner/repo (currently they point to the template).

**Both flavors**

- Update the lab `README.md`: title, one paragraph on what the lab shows, launch links,
  how to run it locally.
- Show the user the final directory tree and the full Dockerfile, and explain each block.

### Step 5: Local build test (always propose this)

Say explicitly why: Binder builds are slow, and the error you find locally in 5 minutes
would take an hour to find online.

```bash
cd <lab-directory>
docker compose -f binder/docker-compose.yml up --build
```

Then open `http://localhost:8888`. Ask the user to check:

- JupyterLab loads, the default notebook opens
- The project imports / launches (run one cell or one command that exercises it)
- For ROS: `ros2 pkg list | grep <pkg>` or `rospack find <pkg>` in a terminal

If the build fails, read the log from the *first* error upward (Docker prints the last
line of a failed command, but the real cause is often higher). Use
`reference/troubleshooting.md`. Fix, rebuild, repeat. Stop with
`docker compose -f binder/docker-compose.yml down`.

Files created inside the container are owned by root; if the user hits permission errors
on the host: `sudo chown -R $USER:$USER <lab-directory>`.

Only skip this step if the user explicitly declines or Docker is unavailable.

### Step 6: Git and GitHub (every action needs a yes)

Explain the goal: the lab must be a **public** GitHub repository so Binder can fetch it.
Then walk through, asking before each command:

1. Initialize the lab repo: `git init -b main` in the lab directory.
2. Review what will be committed (`git status`); warn about large files (videos, meshes,
   datasets over ~50 MB) and secrets.
3. `git add .` and `git commit -m "..."` (propose a message).
4. Create the GitHub repository. Ask **where**: the user's own account or an organization
   (for example `aicor-vrb`). Ask the **name**. Then either
   `gh repo create <owner>/<name> --public --source . --remote origin --push`
   or, without `gh`, describe the browser steps and `git remote add origin <https url>`
   followed by `git push -u origin main`.
5. Submodules, if used: verify `.gitmodules` uses HTTPS URLs.

If the user prefers to do all of this themselves, print the full list of commands and stop.

### Step 7: Launch on Binder and verify

Build the launch URL and show it:

```
https://binder.intel4coro.de/v2/gh/<owner>/<repo>/<branch>?urlpath=lab/tree/<path-to-notebook>
```

- `urlpath=lab/workspaces/new-workspace` opens the saved layout instead of one notebook
- `urlpath=vscode` opens VSCode
- Replace `<branch>` with a tag or commit hash for a frozen, reproducible lab

Tell the user the first launch builds the image and can take a long time; later launches
are fast until the next push (Binder rebuilds when the branch has new commits).

Also add the badge to the README if it is not there yet:

```
[![Binder](https://binder.intel4coro.de/badge_logo.svg)](<launch url>)
```

### Step 8: Listing the lab in the VRB (ask)

The VRB overview page (`https://vrb.ease-crc.org/`) and the aicor-vrb GitHub page bundle
the existing labs. Ask whether the new lab should be listed there. If yes, ask the user
where and how they want it registered (they, or the VRB maintainers, know the process);
prepare a short entry (title, one sentence, launch link) they can submit. Do not attempt
to edit those pages yourself.

## Finishing

End with a short recap: where the lab is on disk, what was built and tested, the launch
URL, and anything still open (untested steps, skipped decisions, known limitations).
