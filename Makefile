o=$(o)

testall:
	@python -m unittest test.test

# e.g. make test o=rename
test:
	@python -m unittest test.test.TestMethods.test_$o

test-options:
	@python -m unittest test.test.TestOptions.test_$o

shell:
	@python3 -m pipenv shell

.PHONY: shell test-options test testall
