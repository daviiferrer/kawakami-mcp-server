.PHONY: dev dev-http build up down logs test lint clean

dev:        ## Roda local com stdio (para OpenCode/Claude Desktop)
	uv run python -m src.main --transport=stdio

dev-http:   ## Roda local com HTTP
	uv run python -m src.main --transport=streamable-http --host=127.0.0.1 --port=8000

build:      ## Build Docker image
	docker compose build

up:         ## Sobe containers (API + tunnel)
	docker compose up -d --build

down:       ## Para containers
	docker compose down

logs:       ## Logs dos containers
	docker compose logs -f

test:       ## Roda testes
	uv run pytest tests/ -v

lint:       ## Lint com ruff
	uv run ruff check src/ tests/

format:     ## Formata codigo
	uv run ruff format src/ tests/

clean:      ## Remove caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache

.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'
