# FAddr

![GitHub](https://img.shields.io/github/license/kido5217/faddr)
![Codacy grade](https://img.shields.io/codacy/grade/0d75ea40d4f544438b4c892036132a04)
![GitHub top language](https://img.shields.io/github/languages/top/kido5217/faddr)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/faddr)

FAddr is a Python program for parsing configuration of network devices such as Juniper and Cisco routers and storing gathered data in database.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install faddr.

```bash
pip install faddr
```

## Usage

Generate database:

```bash
faddr-db -r [RANCID_DIR] -d [DATABASE LOCATION]
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
