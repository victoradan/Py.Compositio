.PHONY: init direnv venv install test types upload

init: venv install direnv

direnv:
	[ -d .envrc ] || echo "source .venv/bin/activate" > .envrc
	direnv allow .

venv:
	[ -d .venv ] || python -m venv .venv

install: venv
	.venv/bin/pip install -r requirements_dev.txt -e .

test:
	pytest --doctest-modules .

types:
	pyright .

upload:
	python -m build
	twine upload dist/*
