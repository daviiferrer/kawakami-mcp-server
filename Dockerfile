FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY src/ ./src/
EXPOSE 8000
CMD ["uv", "run", "python", "-m", "src.main", "--transport=streamable-http", "--host=0.0.0.0", "--port=8000"]
