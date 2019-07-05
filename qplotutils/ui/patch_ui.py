#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import argparse
import fileinput

_log = logging.getLogger("UI patcher")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    arg_parser = argparse.ArgumentParser("UI patcher")
    arg_parser.add_argument("ui")

    args = arg_parser.parse_args()
    ui_file = args.ui

    for line in fileinput.input(ui_file, inplace=True):
        if line.startswith("from PyQt5 "):
            _log.debug("Replaceing PyQt5 with qtpy")
            line = line.replace("from PyQt5 ", "from qtpy ")

        print(line, end="")
