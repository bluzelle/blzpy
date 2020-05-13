![](https://raw.githubusercontent.com/bluzelle/api/master/source/images/Bluzelle%20-%20Logo%20-%20Big%20-%20Colour.png)

### Getting started

Ensure you have a recent version of [Python 3](https://www.python.org/) installed.

Grab the package from github:

    $ pipenv install git+https://github.com/vbstreetz/blzpy.git#egg=bluzelle

Use:

```python
import bluzelle

gas_info = {
  'max_fee': 4000001,
}
client = bluzelle.new_client({
  'address':  '...',
  'mnemonic': '...',
})
client.create('foo', 'bar', gas_info)
value = client.read(key)
client.update(key, 'baz', gas_info)
client.delete(key, gas_info)
```

### Examples

Copy `.env.sample` to `.env` and configure appropriately. You can also use this test [file](https://gist.github.com/vbstreetz/f05a982530311d155836e27d41c1f73a). Then run the example:

```
    DEBUG=false python examples/crud.py
```

### Tests

The `tests/` can best be run in a [pipenv](https://github.com/pypa/pipenv) environment. To do so, initialize one with:

```
    pipenv --python 3
```

Install requirements:

```
    pipenv install
```

Then run the tests:

```
    make test
```

### Licence

MIT
