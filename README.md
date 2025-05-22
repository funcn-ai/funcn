# funcn

A set of beautifully-designed, accessible components and a codebase for building AI-powered applications.

## Summary

Sets up a new development environment for a Mac or Linux (i.e., UNIX) box.

**Table of Contents**

* [funcn](#funcn)
  * [Summary](#summary)
  * [Setup](#setup)
    * [Minimum requirements](#minimum-requirements)
    * [Recommended requirements](#recommended-requirements)
  * [Development](#development)
    * [Devbox](#devbox)
    * [Taskfile](#taskfile)
    * [CLI Usage](#cli-usage)
  * [TODO](#todo)
  * [Further Reading](#further-reading)

## Setup

### Minimum requirements

* [Python 3.11](https://www.python.org/downloads/)

### Recommended requirements

* [devbox](https://www.jetpack.io/devbox/docs/quickstart/)
* [task](https://taskfile.dev/#/installation)

## Development

### Devbox

Devbox takes care of setting up a dev environment automatically.

Under the hood it uses [Nix Package Manager](https://search.nixos.org/packages).

```bash
# install base dependencies
make install

# install devbox
task install-devbox

# enter dev environment w/deps
devbox shell

# run repl
python

# exit dev environment
exit

# run tests
devbox run test
```

### Taskfile

```bash
λ task
task: Available tasks for this project:
* checkbash:                Check bash scripts
* default:                  Default task
* format:                   Run formatters
* install:                  Install project dependencies
* install-devbox:           Install devbox
* lint:                     Run linters
* pre-commit:               Run pre-commit hooks
* pyclean:                  Remove .pyc and __pycache__
* test:                     Run tests
```

### CLI Usage

After installation, you can use the `funcn` command:

```bash
# Show help
funcn --help

# Run the main command
funcn run
```

## TODO

* [Open Issues](https://github.com/greyhaven-ai/funcn/issues)
* For other todo items, see [TODO.md](TODO.md)

## Further Reading

* [python](https://www.python.org/)
* [asdf](https://asdf-vm.com/guide/getting-started.html#_2-download-asdf)
* [docker-compose](https://docs.docker.com/compose/install/)
* [pre-commit hooks](https://pre-commit.com/)
