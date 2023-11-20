VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PY_TEST = $(VENV)/bin/py.test

run: $(VENV)/bin/activate
	$(PYTHON) main.py

test: $(VENV)/bin/activate
	$(PY_TEST) tests

build: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	find . | grep -E "(__pycache__)" | xargs rm -rf