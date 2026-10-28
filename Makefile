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
	rm -rf dist
	python -m build
	twine check dist/*
	twine upload dist/*
