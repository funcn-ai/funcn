---
description: 
globs: 
alwaysApply: true
---
  
  ---
description: Details best practices specific to Python and FastAPI implementations, including recommendations for asynchronous operations, API design, code quality, and performance improvements.
globs: *.py
alwaysApply: false
---

# Running Commands

Follow these guidelines when running commands in this project:

## pip Commands

- all pip commands should be prefixed with `uv` to ensure we are properly accessing our dependencies

## Environment Variables

- Always prefix commands with `doppler run` when access to environment variables is required
- Example: `doppler run python app/main.py` instead of `python app/main.py`
- For development, use: `doppler run --config dev [command]`
- For production, use: `doppler run --config prod [command]`

## Dependency Management

- Use `uv` for all Python dependency management
- Use `task uv:venv` to create a virtual environment
- Use `source .venv/bin/activate` to activate the virual environment
- Use `task uv:install` to install dependencies from pyproject.toml
- Use `task uv:sync` to sync dependencies with lockfile
- Use `task uv:lock` to update the project's lockfile (uv.lock)
- Use `task uv:update-deps` to update dependencies
- Use `task uv:export-reqs` to export requirements.txt

## Task Runner

- Prefer using the task runner for common operations instead of direct commands
- Use `task --list` to see all available tasks
- Use namespaced tasks for specific operations:
  - `task docker:*` for Docker operations
  - `task doppler:*` for Doppler operations
  - `task uv:*` for UV operations
- Common tasks:
  - `task install` - Install project dependencies
  - `task lint` - Run linters
  - `task format` - Run formatters
  - `task test` - Run tests
  - `task docker:build` - Build the Docker image
  - `task docker:up` - Start the project with docker-compose
  - `task doppler:setup` - Setup Doppler

## Development Workflow

1. Set up Doppler: `task doppler:setup`
2. Install dependencies: `task uv:install`
3. Run the application: `doppler run python app/main.py` or use the appropriate task