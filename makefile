.PHONY=

TWINE=$(shell command -v twine 2> /dev/null)

help:
	@echo ERROR: Must provide a make target

docker-build:
	docker build -t 4dgb/4dgbworkflow-build:latest --file build_stage/Dockerfile .

docker-view:
	docker build -t 4dgb/4dgbworkflow-view:latest --file view_stage/Dockerfile .

docker: docker-build docker-view

module:
	rm -rf dist
	rm -rf *.egg-info
	python3 setup.py sdist
	twine upload dist/*
