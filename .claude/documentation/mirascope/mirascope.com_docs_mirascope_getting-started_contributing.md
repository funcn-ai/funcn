---
url: "https://mirascope.com/docs/mirascope/getting-started/contributing"
title: "Contributing | Mirascope"
---

# Contributing [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#contributing)

## Setting Up Development Environment [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#setting-up-development-environment)

We use [uv](https://docs.astral.sh/uv/) as our package and dependency manager.

### Installation [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#installation)

First, install `uv` using the official method:

**macOS and Linux**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**

```
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For more detailed instructions, refer to the [official uv setup guide](https://docs.astral.sh/uv/#getting-started).

### Create a Virtual Environment [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#create-a-virtual-environment)

After installing `uv`, create a virtual environment for development by running:

```
uv sync --all-extras --dev
```

### Pre-commit Setup [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#pre-commit-setup)

To set up pre-commit hooks, run the following command:

```
uv run pre-commit install --install-hooks
```

This will ensure that your code is automatically checked and formatted before each commit.

## Development Workflow [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#development-workflow)

1. Search through existing [GitHub Issues](https://github.com/Mirascope/mirascope/issues) to see if what you want to work on has already been added.
   - If not, please create a new issue. This will help to reduce duplicated work.
2. For first-time contributors, visit [https://github.com/mirascope/mirascope](https://github.com/Mirascope/mirascope) and "Fork" the repository (see the button in the top right corner).


   - You'll need to set up [SSH authentication](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

   - Clone the forked project and point it to the main project:


```
git clone https://github.com/<your-username>/mirascope.git
git remote add upstream https://github.com/Mirascope/mirascope.git
```

3. Development.


   - Make sure you are in sync with the main repo:

```
# for anything that only requires a fix version bump (e.g. bug fixes)
git checkout main
git pull upstream main

# for anything that is "new" and requires at least a minor version bump
git checkout release/vX.Y  # replace X with the current major version and Y with the next minor version
git pull upstream release/vX.Y
```

   - Create a `git` feature branch with a meaningful name where you will add your contributions.

```
git checkout -b meaningful-branch-name
```

   - Start coding! commit your changes locally as you work:

```
git add mirascope/modified_file.py tests/test_modified_file.py
git commit -m "feat: specific description of changes contained in commit"
```

   - Format your code!

```
uv run ruff format .
```

   - Lint and test your code! From the base directory, run:

```
uv run ruff check .
uv run pyright .
```

4. Test!


   - Add tests. Tests should be mirrored based on structure of the source.

```
| - mirascope
|  | - core
|  |  | - openai
|  |  |  | - ...
| - tests
|  | - core
|  |  | - openai
|  |  |  | - ...
```

   - Run tests to make sure nothing is broken

```
uv run pytest tests/
```

   - Check coverage report

```
uv run pytest tests/ --cov=./ --cov-report=html
```

5. Contributions are submitted through [GitHub Pull Requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)


   - When you are ready to submit your contribution for review, push your branch:

```
git push origin meaningful-branch-name
```

   - Open the printed URL to open a PR.
   - Fill in a detailed title and description.
   - Check box to allow edits from maintainers
   - Submit your PR for review. You can do this via Contribute in your fork repo.
   - Link the issue you selected or created under "Development"
   - We will review your contribution and add any comments to the PR. Commit any updates you make in response to comments and push them to the branch (they will be automatically included in the PR)

### Pull Requests [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#pull-requests)

Please conform to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all PR titles and commits.

## Documentation [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#documentation)

We care deeply about maintaining high-quality, up-to-date documentation. This means that all PRs must include corresponding changes to the documentation (if any changes were necessary).

The documentation lives in the [mirascope/website](https://github.com/Mirascope/website) repository.

MacOS Users Will Need cairo

If you're developing using MacOS, you'll need to follow these steps:

1. `brew install cairo`
2. `export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"`
3. `export DYLD_LIBRARY_PATH="/usr/local/lib:/opt/homebrew/lib:$DYLD_LIBRARY_PATH"`
4. `source ~/.bash_profile`

## Testing [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#testing)

All changes to the codebase must be properly unit tested. If a change requires updating an existing unit test, make sure to think through if the change is breaking.

We use `pytest` as our testing framework. If you haven't worked with it before, take a look at [their docs](https://docs.pytest.org/).

Furthermore, we have a full coverage requirement, so all incoming code must have 100% coverage. This policy ensures that every line of code is run in our tests. However, while achieving full coverage is essential, it is not sufficient on its own. Coverage metrics ensure code execution but do not guarantee correctness under all conditions. Make sure to stress test beyond coverage to reduce bugs.

We use a [Codecov dashboard](https://app.codecov.io/github/Mirascope/mirascope/tree/main) to monitor and track our coverage.

## Formatting and Linting [Link to this heading](https://mirascope.com/docs/mirascope/getting-started/contributing\#formatting-and-linting)

In an effort to keep the codebase clean and easy to work with, we use `ruff` for formatting and both `ruff` and `pyright` for linting. Before sending any PR for review, make sure to run both `ruff` and `pyright`.

If you are using VS Code, then install the extensions in `.vscode/extensions.json` and the workspace settings should automatically run `ruff` formatting on save and show `ruff` and `pyright` errors.

Copy as Markdown

#### Provider

OpenAI

#### On this page

Copy as Markdown

#### Provider

OpenAI

#### On this page

## Cookie Consent

We use cookies to track usage and improve the site.

RejectAccept