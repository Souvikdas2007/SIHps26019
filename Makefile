SHELL := /bin/sh
.DEFAULT_GOAL := help

PROJECT_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON = $(if $(shell test -x "$(PROJECT_ROOT)/.venv/bin/python" && printf yes),$(PROJECT_ROOT)/.venv/bin/python,python3)
PIP = "$(PYTHON)" -m pip
NPM ?= npm
BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000
FRONTEND_HOST ?= 127.0.0.1
FRONTEND_PORT ?= 5173
LLAMA_HOST ?= 127.0.0.1
LLAMA_PORT ?= 8080
LLAMA_SERVER ?= /home/mint/Documents/llamac++/llama.cpp/build/bin/llama-server
LLAMA_MODEL ?= $(PROJECT_ROOT)/models/local/SmolLM2-1.7B-Instruct-Q4_K_M.gguf

export PYTHONPATH := $(PROJECT_ROOT)

.PHONY: help setup venv install frontend-install init-db seed admin test build check run run-all backend frontend llama kill clean

help:
	@printf '%s\n' \
		'PS26019 application commands:' \
		'  make setup             Create environment, install dependencies, initialize and seed the database' \
		'  make install           Install Python dependencies in the selected environment' \
		'  make frontend-install  Install frontend dependencies' \
		'  make init-db           Apply SQLite migrations' \
		'  make seed              Create the synthetic offline demo data' \
		'  make admin             Create/update an admin from PS26019_ADMIN_* variables' \
		'  make test              Run backend tests' \
		'  make build             Build the frontend for production' \
		'  make check             Run tests, syntax checks and frontend build' \
		'  make run               Start backend, frontend and local llama.cpp' \
		'  make run-all           Alias for make run' \
		'  make backend           Start only the FastAPI backend' \
		'  make frontend          Start only the Vite frontend' \
		'  make llama             Start only the local llama.cpp server' \
		'  make kill              Stop PS26019 backend, frontend and llama.cpp processes'

setup: venv install frontend-install init-db seed

venv:
	@if [ -x "$(PROJECT_ROOT)/.venv/bin/python" ]; then \
		printf '%s\n' 'Using existing .venv'; \
	else \
		command -v python3 >/dev/null 2>&1 || { echo 'python3 is required'; exit 1; }; \
		python3 -m venv "$(PROJECT_ROOT)/.venv"; \
	fi

install: venv
	$(PIP) install -r "$(PROJECT_ROOT)/requirements.txt"

frontend-install:
	cd "$(PROJECT_ROOT)/frontend" && $(NPM) install

init-db:
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" scripts/init_database.py

seed: init-db
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" scripts/seed_demo.py

admin: init-db
	@test -n "$$PS26019_ADMIN_USERNAME" || { echo 'PS26019_ADMIN_USERNAME is required'; exit 1; }
	@test -n "$$PS26019_ADMIN_PASSWORD" || { echo 'PS26019_ADMIN_PASSWORD is required'; exit 1; }
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" scripts/create_admin.py

test:
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" -m unittest discover -s tests -v

build: frontend-install
	cd "$(PROJECT_ROOT)/frontend" && $(NPM) run build

check: test build
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" -m compileall -q ai backend core scripts tests

backend:
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" -m uvicorn backend.app:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload

frontend:
	cd "$(PROJECT_ROOT)/frontend" && $(NPM) run dev -- --host $(FRONTEND_HOST) --port $(FRONTEND_PORT)

llama:
	@test -x "$(LLAMA_SERVER)" || { echo "llama-server not found or not executable: $(LLAMA_SERVER)"; exit 1; }
	@test -f "$(LLAMA_MODEL)" || { echo "LLAMA_MODEL not found: $(LLAMA_MODEL)"; exit 1; }
	"$(LLAMA_SERVER)" -m "$(LLAMA_MODEL)" --host $(LLAMA_HOST) --port $(LLAMA_PORT)

run:
	@test -x "$(LLAMA_SERVER)" || { echo "llama-server not found or not executable: $(LLAMA_SERVER)"; exit 1; }
	@test -f "$(LLAMA_MODEL)" || { echo "LLAMA_MODEL not found: $(LLAMA_MODEL)"; exit 1; }
	trap 'kill 0' INT TERM EXIT; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	$(MAKE) llama & \
	wait

run-all: run

kill:
	@fuser -k "$(BACKEND_PORT)/tcp" "$(FRONTEND_PORT)/tcp" "$(LLAMA_PORT)/tcp" 2>/dev/null || true
	@pkill -f 'uvicorn backend.app|vite.*--host|llama-server.*--port' 2>/dev/null || true
	@printf '%s\n' 'PS26019 processes stopped.'

clean:
	find "$(PROJECT_ROOT)" -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf "$(PROJECT_ROOT)/frontend/dist" "$(PROJECT_ROOT)/.pytest_cache"
