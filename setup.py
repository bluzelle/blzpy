from setuptools import setup

# from pipenv.project import Project
# from pipenv.utils import convert_deps_to_pip
# pfile = Project(chdir=False).parsed_pipfile
# requirements = convert_deps_to_pip(pfile['packages'], r=False)
# test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)


with open("Readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bluzelle",
    version="0.1.0",
    author="vbstreetz",
    author_email="vbstreetz@gmail.com",
    description=("Python library for the Bluzelle Service."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="bluzelle tendermint cosmos",
    url="https://github.com/vbstreetz/blzpy",
    install_requires=['requests', 'base58', 'ecdsa', 'bech32'],
    packages=['bluzelle'],
    package_dir={'bluzelle': 'lib'},
    classifiers=[
        "Topic :: Utilities",
    ],
    license='MIT License',
    zip_safe=True
)
