### User Acceptance Testing

The following guide describe setting up the project and running an example code and tests in an Ubuntu 18.04 machine. Once ssh'd into the machine:

1. Ensure python3 and pip3 are installed:

```
sudo apt install -y python3 python3-pip
```

2. Install pipenv:

```
pip3 install pipenv
```

Pipenv will be used to create an isolated python environment for the project by not leaking dependencies we'll install to the global scope.

3. Clone and initialize a new pipenv environment for the project:

```
git clone https://github.com/vbstreetz/blzpy.git
cd blzpy
pipenv --python 3
```

4. Activate the virtualenv by spawning a pipenv shell:

```
pipenv shell
```

5. Install all the required dependencies including development related ones:

```
pipenv install --dev
```

These dependencies are specified in the `Pipfile` config.

6. Setup the sample environment variables:

```
cp .env.sample .env
```

The example code and tests will read the bluzelle settings to use from that file i.e. `.env`.

7. Run the example code located at `examples/crud.py`:

```
make example
```

This example code performs simple CRUD operations against the testnet.

8. The project also ships a complete suite of integration tests for all the methods. To run all the tests simply run:

```
make test
```

This will run all the tests in the `test` directory using the same environment settings defined in the `.env` file.
Note that sometimes one or 2 tests fail due to some existing issues with the testnet. A successful run should result in an output like this:

```
...........................
----------------------------------------------------------------------
Ran 27 tests in 285.224s

OK
```
