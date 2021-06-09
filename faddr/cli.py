import argparse
import sys

from faddr.rancid import RancidDir


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r",
        "--rancid-path",
        default="/var/lib/rancid",
        help="Rancid basedir location",
    )

    parser.add_argument(
        "-g",
        "--rancid-groups",
        help="Rancid groups to parse, separated bu coma(,)",
    )

    args = parser.parse_args()
    return vars(args)


def faddr_db():
    args = parse_args()

    rancid = RancidDir(args["rancid_path"])

    if rancid.is_valid() is False:
        error = (
            f'"{args["rancid_path"]}" is not a valid rancid BASEDIR '
            "or was not properly initialised with rancid-csv utility"
        )
        print(error)
        sys.exit(1)

    # Get groups list found in rancid's base dir
    groups = rancid.load_groups(args["rancid_groups"])

    for group in groups:
        rancid.parse_configs(group)
