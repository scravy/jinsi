test:
	python -m unittest

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
