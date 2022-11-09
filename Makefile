.PHONY: all zip ankiweb vendor fix mypy pylint clean
all: zip

ANKIBUILD_ARGS := --qt all --forms-dir forms --exclude user_files/*.json --noconsts

zip:
	python -m ankibuild --type package $(ANKIBUILD_ARGS)

ankiweb:
	python -m ankibuild --type ankiweb $(ANKIBUILD_ARGS)

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
	rm -rf build/
