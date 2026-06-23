FROM node:22-bookworm-slim AS ui-builder

WORKDIR /ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY src/ ./src/
COPY --from=ui-builder /ui/dist ./ui/dist
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "src.main", "--transport=streamable-http", "--host=0.0.0.0", "--port=8000"]
