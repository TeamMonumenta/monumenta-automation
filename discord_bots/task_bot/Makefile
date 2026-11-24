VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

.PHONY: venv test pytest lint typecheck help
.DEFAULT_GOAL := help

# Create .venv and install all dependencies; re-runs pip when the requirements change.
$(VENV)/bin/activate: requirements.txt requirements-dev.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	@touch $@

venv: $(VENV)/bin/activate

test: lint typecheck pytest

pytest: venv
	$(PYTHON) -m pytest tests/ -q

lint: venv
	$(VENV)/bin/pylint taskbot/ main.py cli/ tests/

typecheck: venv
	$(VENV)/bin/pyright

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  venv        Create .venv and install runtime + dev dependencies"
	@echo "  test        Run lint, typecheck, and pytest (stops at first failure)"
	@echo "  lint        Run pylint"
	@echo "  typecheck   Run pyright (strict)"
	@echo "  pytest      Run pytest"
