# Clova Extension Kit SDK for Python

[![PyPI](https://img.shields.io/pypi/v/clova-cek-sdk.svg)](https://pypi.python.org/pypi/clova-cek-sdk)
[![][docs-stable-img]][docs-stable-url]
[![][docs-latest-img]][docs-latest-url]

This is a python library to simplify the use of the Clova Extensions Kit API.

## Documentation

* [Clova Platform Guide](https://clova-developers.line.me/guide/)
* [**STABLE**][docs-stable-url] &mdash; **most recently tagged version of the API documentation.**
* [**LATEST**][docs-latest-url] &mdash; *in-development version of the API documentation.*

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

[docs-latest-img]: https://img.shields.io/badge/docs-latest-blue.svg
[docs-latest-url]: https://clova-cek-sdk-python.readthedocs.io/en/latest/

[docs-stable-img]: https://img.shields.io/badge/docs-stable-blue.svg
[docs-stable-url]: https://clova-cek-sdk-python.readthedocs.io/en/stable/
