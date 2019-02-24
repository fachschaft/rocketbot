
all: mypy lint sort_import

push: update mypy lint verify_import
	git push

update:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt

mypy:
	mypy .

lint:
	flake8 --ignore E501 main.py
	flake8 --ignore E501 rocketbot/
	flake8 --ignore E501 tests/

sort_import:
	isort main.py
	isort -rc rocketbot
	isort -rc tests

verify_import:
	isort --check-only main.py
	isort --check-only -rc rocketbot
	isort --check-only -rc tests
