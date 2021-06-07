import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-r", "--rancid-path", help="Rancid basedir location")

    args = parser.parse_args()
    return args


def faddr_db():
    args = parse_args()
    print(args)
