test:
	python3 -m unittest

venv:
	python3 -m venv .venv

coverage:
	rm -f .coverage
	coverage run --branch --source=jinsi -m unittest discover
	coverage report | tee coverage.txt
	coverage html

install:
	python3 -m pip install -r requirements.txt

clean:
	rm -rf build dist *.egg-info

dist: clean
	python3 setup.py sdist bdist_wheel

publish-test: dist
	python3 -m twine upload --repository testpypi dist/*

publish: dist
	python3 -m twine upload dist/*

.PHONY: test build dist publish clean publish publish-prod
