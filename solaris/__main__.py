import argparse
import datetime as dt
import logging
import os

import solaris
from solaris.config import Config
from solaris import Bot


def parse_args():
    parser = argparse.ArgumentParser("Run Solaris.")
    parser.add_argument("-d", "--debug", help="Run Solaris in debug mode.", action="store_true")
    return parser.parse_args()


def setup_logging(debug):
    if debug:
        level = logging.DEBUG
        filename = "debug.log"
    else:
        level = logging.INFO
        filename = "info.log"

    os.makedirs(solaris.DYNAMIC_DATA_PATH, exist_ok=True)
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(solaris.DYNAMIC_DATA_PATH / filename),
            logging.StreamHandler(),
        ]
    )


if __name__ == "__main__":
    args = parse_args()
    setup_logging(args.debug)
    bot = Bot()
    bot.run()
