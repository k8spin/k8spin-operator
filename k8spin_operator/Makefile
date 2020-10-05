SHELL:=/bin/bash

PROJECTNAME=$(shell basename "$(PWD)")

.PHONY: help install lint
all: help
help: Makefile
	@echo
	@echo " Choose a command run in "$(PROJECTNAME)":"
	@echo
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo

## install: Install the project
install:
	@virtualenv -p python3.8 .venv
	source .venv/bin/activate; \
	pip install -r requirements-dev.txt; \
	pip install -e ../k8spin_common; \


## lint: Lint the project
lint: install
	source .venv/bin/activate; \
	pylint k8spin_operator; \
