SHELL:=/bin/bash

PROJECTNAME=$(shell basename "$(PWD)")

.PHONY: help install lint run kubeconfig
all: help
help: Makefile
	@echo
	@echo " Choose a command run in "$(PROJECTNAME)":"
	@echo
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo

## install: Install the project
install:
	@virtualenv -p python3.9 .venv
	source .venv/bin/activate; \
	pip install -r requirements-dev.txt; \
	pip install -e ../k8spin_common; \

## lint: Lint the project
lint: install
	source .venv/bin/activate; \
	pylint app.py k8spin_reporter; \

## run: Run it locally
run: install kubeconfig resetdb
	source .venv/bin/activate; \
	KUBECONFIG=$(shell pwd)/kubeconfig python app.py

## kubeconfig: Gather k8spin-operator kubeconfig (kind). Requires to run make deploy in the root project
kubeconfig: 
	@kind get kubeconfig --name k8spin-operator > kubeconfig

## resetdb: Reset the database
resetdb:
	@rm -f k8spin.db && sqlite3 k8spin.db < schema.sql
