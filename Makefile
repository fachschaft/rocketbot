FILES=*.py rocketbot tests

all: mypy lint sort_import

run:
	python main.py

push: update utest mypy lint verify_import itest
	git push

update:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt

test: utest itest

utest:
	pytest tests/unit

itest:
	pytest tests/integration

test_cov:
	pytest tests --cov=rocketbot
	codecov

mypy:
	mypy .

lint:
	flake8 $(FILES)

sort_import:
	isort -rc $(FILES)

verify_import:
	isort --check-only -rc $(FILES)

restart_testserver:
	sudo venv/bin/docker-compose -f docker-compose-testserver.yml down && sudo venv/bin/docker-compose -f docker-compose-testserver.yml up -d && until curl http://localhost:3000/api/v1/info; do sleep 5; echo "waiting for Rocket.Chat server to start"; done