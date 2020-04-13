![](https://raw.githubusercontent.com/bluzelle/api/master/source/images/Bluzelle%20-%20Logo%20-%20Big%20-%20Colour.png)

### Getting started

Ensure you have a recent version of [Python 3](https://www.python.org/) installed.

Grab the package from github:

    $ pipenv install git+https://github.com/vbstreetz/blzpy.git#master

Use:

```python
import bluzelle

client = bluzelle.new_client({
    'address':  '...',
    'mnemonic': '...',
    'gas_info': {
      'max_fee': 4000001,
    },
})

key = 'foo'
value = 'bar'

print('creating %s=%s' % (key, value))
try:
    client.create(key, value)
    print('created key')
except bluzelle.APIError as err:
    print('error creating key %s' % (err))
else:
	print()
	print('reading value for key(%s)' % (key))
	try:
	    value = client.read(key)
	    print('read value %s' % (value))
	except bluzelle.APIError as err:
	    print('error reading key %s' % (err))

```

### Licence

MIT
