.PHONY: all zip clean format mypy pylint fix
all: zip

PACKAGE_NAME := asr

zip: $(PACKAGE_NAME).ankiaddon

$(PACKAGE_NAME).ankiaddon: src/*
	rm -f $@
	find src/ -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	( cd src/; zip -r ../$@ * -x meta.json -x user_files/*.json )

vendor:
	pip install -r requirements.txt -t src/vendor

fix:
	python -m black src --exclude="forms|vendor"
	python -m isort src

mypy:
	python -m mypy src

pylint:
	python -m pylint src

clean:
	rm -f $(PACKAGE_NAME).ankiaddon
