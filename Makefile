test:
	@python test/__init__.py -f

shell:
	@python3 -m pipenv shell

.PHONY: shell test
