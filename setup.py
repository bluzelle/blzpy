import os
from setuptools import setup

# from pipenv.project import Project
# from pipenv.utils import convert_deps_to_pip
# pfile = Project(chdir=False).parsed_pipfile
# requirements = convert_deps_to_pip(pfile['packages'], r=False)
# test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bluzelle",
    version = "0.1.0",
    author = "vbstreetz",
    author_email = "vbstreetz@gmail.com",
    description = ("Python library for the Bluzelle Service."),
    keywords = "bluzelle tendermint cosmos",
    url = "https://github.com/vbstreetz/blzpy",
    requires=['requests', 'base58', 'ecdsa'],
    packages=['bluzelle'],
    package_dir = {'bluzelle': 'lib'},
    long_description=read('Readme.md'),
    classifiers=[
        "Topic :: Utilities",
    ],
    license='MIT License',
    zip_safe=True
)
