clean:
	rm -rf dist/

build: clean
	python3 setup.py sdist bdist_wheel

publish: 
	twine upload dist/* --repository cfx-utils

test:
	pytest tests
	pytest separate_tests
