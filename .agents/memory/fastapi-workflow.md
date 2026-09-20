---
name: FastAPI service workflow
description: The API service runs from its artifact directory, so Python module paths in managed workflow commands must be relative to that working directory.
---

Use a file-local Uvicorn target for the Python API service rather than an import path containing the artifact directory name. The managed service command runs with the API artifact as its working directory, while the shared Python environment is resolved from the workspace root.

**Why:** A workspace-relative `--app-dir` made the managed workflow fail to import the FastAPI module even though the same command worked from the repository root.

**How to apply:** Keep the workflow command shaped like `uv run uvicorn fastapi_app:app --host 0.0.0.0 --port $PORT` when the app file lives in the API artifact directory.