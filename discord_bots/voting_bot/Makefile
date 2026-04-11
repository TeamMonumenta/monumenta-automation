VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

.PHONY: venv test lint typecheck help
.DEFAULT_GOAL := help

# Create .venv and install all dependencies.
# Make tracks changes to requirements files -- re-runs pip if they change.
$(VENV)/bin/activate: requirements.txt requirements-dev.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	@touch $@

venv: $(VENV)/bin/activate

test: lint typecheck

lint: venv
	$(VENV)/bin/pylint voting/ main.py bot.py

typecheck: venv
	$(VENV)/bin/pyright

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  venv        Create .venv and install runtime + dev dependencies"
	@echo "  test        Run lint and typecheck"
	@echo "  lint        Run pylint"
	@echo "  typecheck   Run pyright (strict)"
	@echo "  help        Show this message"
