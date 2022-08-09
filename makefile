.PHONY=

TWINE=$(shell command -v twine 2> /dev/null)

help:
	@echo ERROR: Must provide a make target

module:
	rm -rf dist
	rm -rf *.egg-info
	python3 setup.py sdist
	twine upload dist/*
