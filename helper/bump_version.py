#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============
Bump version
============
Script to do housekeeping on version and copyright statemente

"""
import argparse
import logging
import os
import re

_log = logging.getLogger("bump_version")


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


class VersionBumper(object):

    def __init__(self, root):
        if not os.path.exists(root):
            _log.error("Path does not exist.")
            raise IOError()

        self.root = os.path.abspath(root)

        self.__attr = {}
        self.fix_shebang = False
        self.dry_run = False

    @property
    def docstring_attributes(self):
        return self.__attr

    def do_bump(self):
        for dirpath, dirnames, filenames  in os.walk(self.root):
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue

                full_path = os.path.join(dirpath, filename)
                _log.debug("Fullpath: {}".format(full_path))

                self.apply(full_path)


    def apply(self, filepath):
        with open(filepath, "r") as fp:
            contents = fp.readlines()

        contents = self.update_docstring_parameters(contents)
        if self.fix_shebang:
            contents = self.fix_file_header(contents)

        if self.dry_run:
            print("\n-------------------------------------------------------\n"
                  "FILE:", filepath)
            print("".join(contents))
            return

        with open(filepath, "w") as fp:
            for row in contents:
                fp.write(row)

    def update_docstring_parameters(self, contents):
        ptr = re.compile("^\_\_(\w+)\_\_\s+\=.+$")

        updated_contents = []
        for line in contents:
            m = ptr.match(line)
            if m and m.group(1) in self.docstring_attributes:
                k = m.group(1)
                v = self.docstring_attributes[k]
                if isinstance(v, (list, tuple)):
                    updated_line = '__{}__ = {}'.format(k, v)
                else:
                    updated_line = '__{}__ = "{}"'.format(k, v)
                # print(updated_line)
                updated_contents.append(updated_line + "\n")

            else:
                updated_contents.append(line)

        # print(updated_contents)
        return updated_contents

    def fix_file_header(self, contents):

        updated_contents = contents

        py_hdr_01 = """#!/usr/bin/env python3\n"""
        py_hdr_02 = """# -*- coding: utf-8 -*-\n"""

        if len(contents) == 0:
            updated_contents.append(py_hdr_01)
            updated_contents.append(py_hdr_02)
            return  updated_contents

        if contents[0] != py_hdr_01:
            if contents[0].startswith("#!"):
                # Has shebang, update:
                updated_contents[0] = py_hdr_01
            else:
                updated_contents.insert(0, py_hdr_01)
        if contents[1] != py_hdr_02:
            if contents[1].startswith("# -*-"):
                # Has coding string, update:
                updated_contents[1] = py_hdr_02
            else:
                updated_contents.insert(1, py_hdr_02)

        return updated_contents


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="path", type=str, help="File or path where to bump versions")
    parser.add_argument(dest="next_version", type=str, help="Sets the given version")
    parser.add_argument("--copyright", dest="copyright",  type=str)
    parser.add_argument("--fix-shebang", dest="fix_shebang", action='store_true')
    parser.add_argument("--dry-run", dest="dry_run", action='store_true')
    args = parser.parse_args()



    vb = VersionBumper(args.path)
    vb.fix_shebang = args.fix_shebang
    vb.dry_run = args.dry_run

    vb.docstring_attributes["version"] = args.next_version
    if args.copyright:
        vb.docstring_attributes["copyright"] = args.copyright

    vb.do_bump()


