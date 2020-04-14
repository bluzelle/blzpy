o=$(o)

testall:
	@python test/__init__.py -f

# e.g. make test o=rename
test:
	@python -m unittest test.test.TestMethods.test_$o

shell:
	@python3 -m pipenv shell

.PHONY: shell test testall
