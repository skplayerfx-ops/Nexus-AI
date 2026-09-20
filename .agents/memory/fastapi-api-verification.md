---
name: FastAPI API verification
description: Environment-specific guidance for verifying FastAPI endpoints in this workspace.
---

The installed Starlette TestClient expects the optional `httpx2` package. When it is unavailable, verify FastAPI endpoints through the managed Uvicorn workflow with local HTTP requests instead of changing project dependencies for a one-off test.

**Why:** Adding a testing dependency solely to exercise a small API change can alter the workspace environment unnecessarily; the running service provides a closer end-to-end check.

**How to apply:** Compile the module first, restart the API workflow after server changes, then use the workflow's local port to check representative success and validation responses.