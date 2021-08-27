import argparse
import sys

from faddr.rancid import RancidDir
from faddr.database import Database


def parse_args_db():
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

    parser.add_argument(
        "-d",
        "--database-file",
        default="/var/db/faddr/faddr.json",
        help="TinyDB file location",
    )

    args = parser.parse_args()
    return vars(args)


def faddr_db():
    args = parse_args_db()

    rancid = RancidDir(args["rancid_path"])

    db = Database(args["database_file"])

    if not rancid.is_valid():
        error = (
            f'"{args["rancid_path"]}" is not a valid rancid BASEDIR '
            "or was not properly initialised with rancid-csv utility"
        )
        print(error)
        sys.exit(1)

    # Get groups list found in rancid's base dir
    groups = rancid.load_groups(args["rancid_groups"])

    for group in groups:
        data = rancid.parse_configs(group)
        if len(data) > 0:
            db.insert(data)
