o=$(o)

test:
	@$(MAKE) test-options-all
	@$(MAKE) test-methods-all

test-methods-all:
	@python -m unittest test.methods.TestMethods

test-options-all:
	@python -m unittest test.options.TestOptions

# e.g. make test o=rename
test-methods:
	@python -m unittest test.methods.TestMethods.test_$o

test-options:
	@python -m unittest test.options.TestOptions.test_$o

example:
	@python examples/crud.py

shell:
	@python3 -m pipenv shell

.PHONY: test \
	test-methods-all \
	test-options-all \
	test-methods \
	test-options \
	example \
	shell
