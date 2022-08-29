.PHONY=

TWINE=$(shell command -v twine 2> /dev/null)
VERSION=$(shell awk 'NR==1{print $1}' version.txt)

help:
	@echo ERROR: Must provide a make target

docker-build:
	docker build -t 4dgb/4dgbworkflow-build:latest --file build_stage/Dockerfile .

docker-view:
	docker build -t 4dgb/4dgbworkflow-view:latest --file view_stage/Dockerfile .

docker: docker-build docker-view

docker-tag:
	docker tag 4dgb/4dgbworkflow-build:latest 4dgb/4dgbworkflow-build:${VERSION}
	docker tag 4dgb/4dgbworkflow-view:latest 4dgb/4dgbworkflow-view:${VERSION}
	docker push 4dgb/4dgbworkflow-build:latest
	docker push 4dgb/4dgbworkflow-build:${VERSION}
	docker push 4dgb/4dgbworkflow-view:latest
	docker push 4dgb/4dgbworkflow-view:${VERSION}

module:
	rm -rf dist
	rm -rf *.egg-info
	python3 setup.py sdist

module-upload:
	twine upload dist/*
