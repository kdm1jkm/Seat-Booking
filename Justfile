UV_RUN := "uv run --locked"

run:
	{{UV_RUN}} main.py

fix:
	{{UV_RUN}} ruff check --fix .
	{{UV_RUN}} ruff format .

check:
	{{UV_RUN}} ruff format --check .
	{{UV_RUN}} ruff check .
	{{UV_RUN}} ty check

format:
	{{UV_RUN}} ruff format .
