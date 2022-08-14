# mutwo.mbrola

[![Build Status](https://circleci.com/gh/mutwo-org/mutwo.mbrola.svg?style=shield)](https://circleci.com/gh/mutwo-org/mutwo.mbrola)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/mutwo.mbrola.svg)](https://badge.fury.io/py/mutwo.mbrola)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Mbrola extension for [mutwo](https://github.com/mutwo-org/mutwo).

### Installation

mutwo.mbrola is available on [pypi](https://pypi.org/project/mutwo.mbrola/) and can be installed via pip:

```sh
pip3 install mutwo.mbrola
```

### Limitations

Mbrola has problems with long durations of single phonemes (longer than around 8 seconds).
Sometimes it will just produce empty sound files in this case.
It is not clear yet what's the border, maybe in the mbrola documentation one can find more about this.
