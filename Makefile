.PHONY: up down db db-reset psql test lint fmt api ui-admin ui-chat

up:
	docker compose up -d --build

down:
	docker compose down

db:
	docker compose up -d postgres

db-reset:
	docker compose rm -sf postgres
	docker volume rm -f lexfold_pgdata
	docker compose up -d postgres

psql:
	docker compose exec postgres psql -U lexfold -d lexfold

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check .

fmt:
	.venv/bin/ruff format .

api:
	DATABASE_URL=postgresql://lexfold:lexfold@localhost:5432/lexfold .venv/bin/uvicorn api.main:app --reload

ui-admin:
	.venv/bin/streamlit run ui/admin_app.py --server.port 8502

ui-chat:
	.venv/bin/streamlit run ui/chat_app.py --server.port 8501
