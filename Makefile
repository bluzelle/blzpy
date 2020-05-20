o=$(o)

test:
	@$(MAKE) test-all-options
	@$(MAKE) test-all-methods

test-all-methods:
	@python -m unittest --failfast test.methods

test-all-options:
	@python -m unittest --failfast test.options

# e.g. make test o=rename
test-methods:
	@python -m unittest --failfast test.methods.TestMethods.test_$o

test-options:
	@python -m unittest --failfast test.options.TestOptions.test_$o

example:
	@python examples/crud.py

shell:
	@~/homebrew/bin/python3 -m pipenv shell

deploy:
	@python setup.py sdist bdist_wheel
	@twine upload dist/*

uat:
	@FLASK_APP="uat:app" FLASK_ENV=development flask run --port=4561

.PHONY: test \
	test-all-methods \
	test-all-options \
	test-methods \
	test-options \
	example \
	shell \
	deploy \
	uat
