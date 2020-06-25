init:
	pip install -r requirements.txt

test:
	cd tests && pytest

lint:
	pylint websitemonitor/*.py

docker:
	docker build -f ./docker/Dockerfile -t websitemonitor .

.PHONY: init test lint docker

