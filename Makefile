SHELL := /bin/sh
MAKEFLAGS += Rrs

.ONESHELL:
.SUFFIXES:

.DEFAULT_GOAL := help

VENV := venv
BIN := $(VENV)/bin

PIP := $(BIN)/pip

MYPY := $(BIN)/mypy
PYLINT := $(BIN)/pylint
PYTEST := $(BIN)/pytest

.PHONY: help
help:
	echo 'Usage: make <target>'
	echo ''
	echo 'Targets:'
	echo '  dockerize              Build a Docker image for the scanner'
	echo '  lint                   Lint `*.py` source files'
	echo '  test                   Run tests'
	echo '  start-selenium-server  Start a Selenium server for local testing'
	echo '  stop-selenium-server   Stop the Selenium server'
	echo ''

.PHONY:
dockerize:
	docker build -t upwork-scanner .

.PHONY:
lint: $(VENV)
	$(PYLINT) upwork
	$(MYPY) -m upwork

.PHONY: test
test: $(VENV) start-selenium-server
	$(PYTEST) -v tests

.PHONY: start-selenium-server
start-selenium-server:
	docker compose up -d

.PHONY: stop-selenium-server
stop-selenium-server:
	docker compose down

$(VENV):
	python3 -m venv $@
	$(PIP) install -r requirements-dev.txt
