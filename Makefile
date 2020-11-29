dist:
	python3 setup.py sdist bdist_wheel

publish:
	python3 -m twine upload --repository testpypi dist/*

publish-prod:
	python3 -m twine upload dist/*

.PHONY: dist publish

