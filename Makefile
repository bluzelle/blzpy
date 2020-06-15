o=$(o)

test:
	@$(MAKE) test-options
	@$(MAKE) test-methods

test-methods:
	@python -m unittest --failfast test.methods -vv

test-options:
	@python -m unittest --failfast test.options -vv

# e.g. make test-method o=rename
test-method:
	@python -m unittest --failfast test.methods.TestMethods.test_$o -vv

test-option:
	@python -m unittest --failfast test.options.TestOptions.test_$o -vv

example:
	@python examples/crud.py

shell:
	@~/homebrew/bin/python3 -m pipenv shell

pip:
	@~/homebrew/bin/python3 -m pipenv install --dev

deploy:
	@python setup.py sdist bdist_wheel
	@twine upload dist/*

uat:
	@FLASK_APP="uat:app" FLASK_ENV=development flask run --port=4561

.PHONY: test \
	test-methods \
	test-options \
	test-method \
	test-option \
	example \
	shell \
	deploy \
	pip \
	uat
