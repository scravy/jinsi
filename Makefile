dist:
	python3 setup.py sdist bdist_wheel

publish:
	python3 -m twine upload --repository testpypi dist/*

publish-prod:
	python3 -m twine upload dist/*

clean:
	rm -rf build dist *.egg-info

.PHONY: dist publish

