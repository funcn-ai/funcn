#!/usr/bin/make -f

.DEFAULT_GOAL := help

.ONESHELL:

# ENV VARS
export SHELL := $(shell which sh)
export UNAME := $(shell uname -s)
export ARCH  := $(shell uname -m)
export ASDF_VERSION := v0.15.0
export DEBIAN_FRONTEND := noninteractive
export DEBCONF_NOWARNINGS := yes
export DEBCONF_TERSE := yes

# check commands and OS
ifeq ($(UNAME), Darwin)
	export XCODE := $(shell xcode-select -p 2>/dev/null)
	export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK := 1
else ifeq ($(UNAME), Linux)
	-include /etc/os-release
endif

# set arch for binary downloads
ifeq ($(ARCH), aarch64)
	export ARCH := arm64
else ifeq ($(ARCH), arm64)
	export ARCH := arm64
else ifeq ($(ARCH), x86_64)
	export ARCH := amd64
endif

# colors
GREEN := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE := $(shell tput -Txterm setaf 7)
CYAN := $(shell tput -Txterm setaf 6)
RESET := $(shell tput -Txterm sgr0)

# Usage: $(call check_bin,command_name)
# Returns empty string if command not found, command path if found
define check_bin
	$(shell which $(1) 2>/dev/null)
endef

# Usage: $(call brew_install,package_name)
# For packages where binary name differs from package name, add a mapping in the case statement
define brew_install
	@if [ "${UNAME}" = "Darwin" ] || [ "${UNAME}" = "Linux" ]; then \
		binary_name=""; \
		case "$(1)" in \
			"go-task") binary_name="task" ;; \
			*) binary_name="$(1)" ;; \
		esac; \
		if ! command -v $$binary_name >/dev/null 2>&1; then \
			echo "Installing $(1)..."; \
			brew install $(1); \
		else \
			echo "$(1) already installed."; \
		fi \
	else \
		echo "$(1) not supported."; \
	fi
endef

# targets
.PHONY: all
ifeq ($(UNAME), Darwin)
all: help asdf xcode brew jq pre-commit task yq ## [Darwin] run all targets for macOS
else ifeq ($(UNAME), Linux)
all: help jq pre-commit task yq ## [Linux] run all targets for Linux
else
all: help ## [Other] show help
	@echo "This platform is not fully supported."
endif

xcode: ## install xcode command line tools
ifeq ($(UNAME), Darwin)
	@if [ -z "${XCODE}" ]; then \
		echo "Installing Xcode command line tools..."; \
		xcode-select --install; \
	else \
		echo "xcode already installed."; \
	fi
else
	@echo "xcode not supported."
endif

brew: xcode ## install homebrew
ifeq ($(UNAME), Darwin)
	@if ! command -v brew >/dev/null 2>&1; then \
		echo "Installing Homebrew..."; \
		NONINTERACTIVE=1 /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null 2>&1; \
	else \
		echo "brew already installed."; \
	fi
else ifeq ($(UNAME), Linux)
	@if [ "${ID}" = "debian" ] || [ "${ID_LIKE}" = "debian" ]; then \
		if ! command -v brew >/dev/null 2>&1; then \
			echo "Installing Homebrew..."; \
			NONINTERACTIVE=1 /bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" > /dev/null 2>&1; \
			echo ""; \
			echo "To add Homebrew to your PATH, run these commands:"; \
			echo 'eval "$$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"'; \
			echo 'Add to ~/.profile or ~/.bashrc:'; \
			echo 'eval "$$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"'; \
		else \
			echo "brew already installed."; \
		fi \
	else \
		echo "brew not supported on this Linux distribution."; \
	fi
else
	@echo "brew not supported."
endif

asdf: xcode ## install asdf
	@if ! command -v asdf >/dev/null 2>&1; then \
		echo "Installing asdf..."; \
		git clone -q https://github.com/asdf-vm/asdf.git ~/.asdf --branch ${ASDF_VERSION} > /dev/null 2>&1; \
		echo "To use asdf, add the following to your shell rc (.bashrc/.zshrc):"; \
		echo "export PATH=\"$$HOME/.asdf/shims:$$PATH\""; \
		echo ". $$HOME/.asdf/asdf.sh"; \
		echo ". $$HOME/.asdf/completions/asdf.bash"; \
	else \
		echo "asdf already installed."; \
	fi

jq: ## install jq
ifeq ($(UNAME), Darwin)
	@$(call brew_install,jq)
else ifeq ($(UNAME), Linux)
	@echo "Installing jq..."
	@sudo apt-get update -qq > /dev/null 2>&1 && sudo apt-get install -y -qq --no-install-recommends jq > /dev/null 2>&1
else
	@echo "jq not supported on this platform."
endif

pre-commit: ## install pre-commit
ifeq ($(UNAME), Darwin)
	@$(call brew_install,pre-commit)
else ifeq ($(UNAME), Linux)
	@echo "Installing pre-commit..."
	@uv pip install -q pre-commit > /dev/null 2>&1
else
	@echo "pre-commit not supported on this platform."
endif

task: ## install taskfile
ifeq ($(UNAME), Darwin)
	@$(call brew_install,go-task)
else ifeq ($(UNAME), Linux)
	@echo "Installing task..."
	@sh -c "$$(curl -s --location https://taskfile.dev/install.sh)" -- -d -b $(HOME)/.local/bin > /dev/null 2>&1
else
	@echo "task not supported on this platform."
endif

yq: ## install yq
ifeq ($(UNAME), Darwin)
	@$(call brew_install,yq)
else ifeq ($(UNAME), Linux)
	@echo "Installing yq..."
	@DEBIAN_FRONTEND=noninteractive sudo wget -q https://github.com/mikefarah/yq/releases/latest/download/yq_linux_${ARCH} -O /usr/bin/yq > /dev/null 2>&1 && DEBIAN_FRONTEND=noninteractive sudo chmod +x /usr/bin/yq > /dev/null 2>&1
else
	@echo "yq not supported on this platform."
endif

# Platform-specific install targets
.PHONY: install configure-apt

configure-apt: ## Configure apt to be silent
ifeq ($(UNAME), Linux)
	@if [ -d /etc/apt ]; then \
		echo 'Dpkg::Use-Pty "0";' | sudo tee /etc/apt/apt.conf.d/00silent > /dev/null 2>&1 || true; \
		echo 'APT::Get::Assume-Yes "true";' | sudo tee -a /etc/apt/apt.conf.d/00silent > /dev/null 2>&1 || true; \
		echo 'APT::Get::quiet "true";' | sudo tee -a /etc/apt/apt.conf.d/00silent > /dev/null 2>&1 || true; \
	fi
	@if command -v debconf-set-selections > /dev/null 2>&1; then \
		echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections > /dev/null 2>&1 || true; \
	fi
endif

ifeq ($(UNAME), Darwin)
install: xcode asdf brew jq pre-commit task yq ## [Darwin] install dependencies
else ifeq ($(UNAME), Linux)
install: configure-apt jq pre-commit task yq ## [Linux] install dependencies for Linux
else
install: ## [Other] install dependencies
	@echo "Installation not supported on this platform."
endif

help: ## show this help
	@echo ''
	@echo 'Usage:'
	@echo '    ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk -v uname="${UNAME}" 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) { \
			target=$$1; \
			desc=$$2; \
			if (match(desc, /^\[(Darwin|Linux|Other)\]/)) { \
				platform=substr(desc, RSTART+1, RLENGTH-2); \
				if (platform == uname || (platform == "Other" && uname != "Darwin" && uname != "Linux")) { \
					gsub(/^\[(Darwin|Linux|Other)\] /, "", desc); \
					printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", target, desc; \
				} \
			} else { \
				printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", target, desc; \
			} \
		} else if (/^## .*$$/) { \
			printf "  ${CYAN}%s${RESET}\n", substr($$1,4); \
		} \
	}' $(MAKEFILE_LIST)
