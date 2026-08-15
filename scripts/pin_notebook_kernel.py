#!/usr/bin/env python3
"""Point generated notebooks at the kernel this image actually has.

jupytext writes whatever kernelspec the exercise source declares (`Python 3` / `python3`).
The lab's kernel is the conda one registered by the base image, and VSCode's Jupyter
extension picks a kernel for a freshly opened notebook by matching the notebook's
kernelspec against the installed ones -- a display name that does not match ("Python 3"
vs "Python 3 (ipykernel)") is enough to leave a learner on "Select Kernel". Rewriting the
metadata to the installed spec makes the match exact, in JupyterLab as well.

Usage: pin_notebook_kernel.py <directory-of-notebooks> [kernel-name]
"""

import json
import sys
from pathlib import Path

from jupyter_client.kernelspec import KernelSpecManager, NoSuchKernel


def installed_kernelspec(name: str) -> dict:
    """The kernelspec `name` as this interpreter's Jupyter has it installed."""
    manager = KernelSpecManager()
    try:
        spec = manager.get_kernel_spec(name)
    except NoSuchKernel:
        raise SystemExit(
            f"kernel {name!r} is not installed; available: "
            f"{sorted(manager.find_kernel_specs())}"
        )
    return {
        "name": name,
        "display_name": spec.display_name,
        "language": spec.language,
    }


def main() -> None:
    directory = Path(sys.argv[1])
    kernel_name = sys.argv[2] if len(sys.argv) > 2 else "python3"
    kernelspec = installed_kernelspec(kernel_name)

    notebooks = sorted(directory.glob("*.ipynb"))
    if not notebooks:
        raise SystemExit(f"no notebooks in {directory}")

    for notebook in notebooks:
        content = json.loads(notebook.read_text())
        content.setdefault("metadata", {})["kernelspec"] = kernelspec
        notebook.write_text(json.dumps(content, indent=1, ensure_ascii=False) + "\n")
        print(f"{notebook.name}: kernel -> {kernelspec['display_name']}")


if __name__ == "__main__":
    main()
