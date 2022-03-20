# FAddr

[![CodeFactor](https://www.codefactor.io/repository/github/kido5217/faddr/badge)](https://www.codefactor.io/repository/github/kido5217/faddr)
[![GitHub top language](https://img.shields.io/github/languages/top/kido5217/faddr)](https://www.python.org/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/faddr)](https://pypi.org/project/faddr/)
[![GitHub](https://img.shields.io/github/license/kido5217/faddr)](https://opensource.org/licenses/MIT)

FAddr is a Python program for parsing configuration of network devices such as Juniper and Cisco routers and storing gathered data in database.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install faddr.

```bash
pip install faddr
```

## Usage

Generate database:

```bash
faddr-db
```

Find ip address termination point:

```bash
faddr 10.20.30.1
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
