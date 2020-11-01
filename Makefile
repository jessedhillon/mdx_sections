VENV_NAME   ?=venv
VENV_ACTIVATE=. ${VENV_NAME}/bin/activate
PYTHON       =${VENV_NAME}/bin/python3
PYLINT_FLAGS =--disable=attribute-defined-outside-init

.PHONY: help prepare-dev pylint isort black format

.DEFAULT: help
help:
	@echo ""
	@echo "make prepare-dev: prepare development environment, use only once."
	@echo "make pylint: lint with pylint."
	@echo "make isort: sort Python imports."
	@echo "make black: format the Python project."
	@echo "make format: sort Python imports and format the Python project."
	@echo ""

prepare-dev:
	python3 -m pip install virtualenv
	make venv

venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: setup.py
	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install pip -U
	${PYTHON} -m pip install --use-feature=2020-resolver -e .
	${PYTHON} -m pip install --use-feature=2020-resolver -r require_dev.txt -U
	touch $(VENV_NAME)/bin/activate

pylint: venv
	${PYTHON} -m pylint mdx_sections/ ${PYLINT_FLAGS} || true

isort: venv
	${PYTHON} -m isort . --force-single-line

black: venv
	${PYTHON} -m black .

format: isort black
