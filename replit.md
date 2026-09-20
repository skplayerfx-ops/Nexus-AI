# Nexus-AI

Nexus-AI is a focused conversation workspace for thinking, planning, and drafting with an assistant.

## Run & Operate

- `uv run uvicorn main:app --host 0.0.0.0 --port $PORT` — run the FastAPI service
- `pnpm --filter @workspace/nexus-ai run dev` — run the web app
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- Python dependencies are managed by `uv` in the workspace `pyproject.toml`.

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: FastAPI + Uvicorn
- Frontend: React + Vite + Tailwind CSS
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `main.py` — FastAPI routes and in-memory conversation state
- `index.html` — standalone frontend UI and browser interactions
- `requirements.txt` — Python runtime dependencies
- `lib/api-spec/openapi.yaml` — source of truth for API contracts
- `artifacts/nexus-ai/` — preview configuration for the root `index.html`

## Architecture decisions

- The FastAPI service keeps a small in-memory seed dataset for the first build so the workspace is useful immediately without a database setup.
- The browser UI uses the FastAPI routes directly with `fetch`, keeping the user-facing app in one HTML file.
- The preview server serves the root `index.html`; the FastAPI service remains the source for `/api` routes.

## Product

Users can browse seeded conversations, open a thread, start a new conversation, send prompts, receive assistant responses, and adjust interface preferences from Settings.

## User preferences

No additional preferences recorded.

## Gotchas

- Re-run API codegen after changing `lib/api-spec/openapi.yaml`.
- Conversation data is currently process-local and resets when the API service restarts.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
