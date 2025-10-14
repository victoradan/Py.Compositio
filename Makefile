.PHONY: direnv venv install test init

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
