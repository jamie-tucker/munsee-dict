VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PY_TEST = $(VENV)/bin/py.test

.PHONY: run test clean build

run: build
	$(PYTHON) main.py

test: build
	$(PY_TEST) tests

build: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	mkdir -p data/input
	mkdir -p data/output
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	find . | grep -E "(__pycache__)" | xargs rm -rf