# Clova Extension Kit SDK for Python

[![PyPI](https://img.shields.io/pypi/v/clova-cek-sdk.svg)](https://pypi.python.org/pypi/clova-cek-sdk)

This is a python library to simplify the use of the Clova Extensions Kit API.

## Documentation

* [Clova Platform Guide](https://clova-developers.line.me/guide/)
* [Clova Extension Python SDK API](https://line.github.io/clova-cek-sdk-python/)

## Installation

```
pip install clova-cek-sdk
```

## Development

### Run Tests

```
python -m unittest discover -s ./test -p 'test_*.py'
```

### Building docs locally

#### Requirements

```
pip install -e '.[docs]'
```

#### Build

```
sphinx-versioning build docs docs/_build/html
```

#### Push

```
sphinx-versioning push docs gh-pages .
```
