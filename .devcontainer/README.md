# devcontainers

[Microsoft describes dev containers](https://code.visualstudio.com/docs/devcontainers/containers) (shortened to `devcontainers`) as:

> The Visual Studio Code Dev Containers extension lets you use a container as a full-featured development environment. It allows you to open any folder inside (or mounted into) a container and take advantage of Visual Studio Code's full feature set. A [devcontainer.json](https://code.visualstudio.com/docs/devcontainers/containers#_create-a-devcontainerjson-file) file in your project tells VS Code how to access (or create) a development container with a well-defined tool and runtime stack. This container can be used to run an application or to separate tools, libraries, or runtimes needed for working with a codebase.
> 
> Workspace files are mounted from the local file system or copied or cloned into the container. Extensions are installed and run inside the container, where they have full access to the tools, platform, and file system. This means that you can seamlessly switch your entire development environment just by connecting to a different container.
>
> ![devcontainers architecture](architecture.png)
> 
> This lets VS Code provide a local-quality development experience including full IntelliSense (completions), code navigation, and debugging regardless of where your tools (or code) are located.

## Minimum requirements

* [Docker](https://www.docker.com/)
* [VS Code](https://code.visualstudio.com/)
* [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Usage

### Reopen in container

Open the command palette (Ctrl+Shift+P or Cmd+Shift+P) and select `Dev Containers: Reopen in Container`.

To verify that the container is running, open the terminal and run `cat /etc/os-release`.

```bash
appuser@dba67b5ddabf:/app$ cat /etc/os-release 
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
```

### Reopen folder locally

Open the command palette (Cmd-Shift-P or Ctrl-Shift-P) and select `Dev Containers: Reopen Folder Locally`.

### Activate virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml --all-extras
```

### Start the application in development mode

```bash
doppler run -p medprodigy-rec-sys -c dev -- uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Check Health Endpoint

```bash
curl -H "X-API-Key: ${API_KEY}" http://localhost:8000/health
```

### Access the API docs

```bash
curl -H "X-API-Key: ${API_KEY}" http://localhost:8000/docs
```

### Run tests

```bash
task test
```

## Development

[devcontainer.json](devcontainer.json) is pointed to the top-level [Dockerfile.dev](../Dockerfile.dev). This can later be changed to use docker compose with an [extended configuration](docker-compose.extend.yml) to cache the workspace, enable debugging system traces, and make unrestricted system calls.

Notable `devcontainer.internal.json` properties:

* `workspaceFolder`: the path to the workspace folder in the container
* `containerEnv`: environment variables to set in the container
* `remoteUser`: the user to use in the container
* `extensions`: VS Code extensions to install in the container
  * These can be added from the extensions view by right clicking an extension and selecting "Add to devcontainer.json"
* `features`: devcontainer [features](https://containers.dev/features) to install in the container
* `forwardPorts`: ports to forward from the container to the local machine
