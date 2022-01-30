"""CLI entry points of faddr."""

import argparse

from faddr import logger
from faddr.rancid import RancidDir
from faddr.settings import Settings


def parse_args_db():
    """Parsing CMD keys."""
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

    parser.add_argument(
        "-s",
        "--settings-file",
        help="Faddr settings file  location",
    )

    args = parser.parse_args()
    return vars(args)


def faddr_db():
    """Parsing devices' config files and writing data to database."""
    args = parse_args_db()
    logger.debug(f"Arguments from CMD: {args}")
    settings = Settings()

    # config = load_config(cmd_args=args)

    # rancid = RancidDir(config.rancid.dir)
    # for group in rancid.groups:
    #    print(group.configs)
    print(settings)
