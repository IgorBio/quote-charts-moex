VENV_NAME := venv
PYTHON := $(VENV_NAME)/bin/python3
PIP := $(VENV_NAME)/bin/pip3

all: venv

venv: requirements.txt
	python3 -m venv $(VENV_NAME)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
	rm -rf $(VENV_NAME)