import os
import re
import itertools

import sublime_plugin

from .CeedlingSettings import CeedlingProjectSettings
from . import glob2


class CeedlingPathBuilder:
    def __init__(self, settings):
        self.conf = settings

    def split_name(self, filename):
        """Return dict of file name components."""
        result = re.search(
            r"(?P<prefix>{})?".format(self.conf.test_file_prefix)
            + r"(?P<base>.+?)\."
            + r"(?P<ext>{}|{})$".format(
                self.conf.source_ext, self.conf.header_ext
            ),
            filename,
        )
        return {} if result is None else result.groupdict()

    def build_path(self, option, base):
        # todo: Check this assumption holds when env is set
        working_dir = self.conf.working_dir
        ext = self.conf.source_ext

        if working_dir is None:
            raise IOError("missing path")

        if option == "test":
            included = self.conf.test
            excluded = self.conf.test_excl
            base = "".join((self.conf.test_file_prefix, base))

        elif option == "source":
            included = self.conf.source
            excluded = self.conf.source_excl

        else:
            included = self.conf.includes
            excluded = self.conf.includes_excl
            ext = self.conf.header_ext

        # Build list of matching files within configured directories
        file_list = list(
            self._glob_search(included, working_dir, base, ext)
            - self._glob_search(excluded, working_dir, base, ext)
        )

        if len(file_list) == 0:
            raise IOError("No matching file")

        elif len(file_list) > 1:
            print("Duplicate matches found:")

            for dup in file_list:
                print(dup)

        return file_list[0]

    def _glob_search(self, pattern, path, base, ext):
        """Return set of files matching glob path.

        Ceedling project.yml uses globstar `**` pattern.
        This is not supported by Python before v3.5.
        `glob2` module backports this functionality to earlier Python versions
        and is used to maintain Sublime Text 3 support.
        """
        return set(
            itertools.chain.from_iterable(
                glob2.iglob(
                    os.path.abspath(
                        os.path.join(
                            path,
                            os.path.normpath(p),
                            ".".join((base, ext)),
                        )
                    ),
                    recursive=True,
                )
                for p in pattern
            )
        )


class CeedlingOpenFileCommand(sublime_plugin.WindowCommand):
    def run(self, option):

        self.views = []
        window = self.window

        variables = self.window.extract_variables()

        if not self.window.active_view():
            return

        try:
            self.conf = CeedlingProjectSettings(self.window)
            self.pathbuilder = CeedlingPathBuilder(self.conf)

        except OSError as e:
            self.window.status_message("Ceedling: %s" % e)
            return

        if option == "config":
            return self._open_file(self.conf.project_yml)

        # Extract file name components
        filename = self.pathbuilder.split_name(variables.get("file_name"))

        if filename is None:
            self.window.status_message("Ceedling switching: unsupported file")
            return

        # Filename less extension and test prefix
        base_name = filename.get("base")

        try:
            if option == "next":
                if filename.get("prefix") == self.conf.test_file_prefix:
                    option = "source"
                elif filename.get("ext") == self.conf.source_ext:
                    option = "header"
                else:
                    option = "test"

            if option == "test_and_source":
                window.run_command(
                    "set_layout",
                    {
                        "cols": [0.0, 0.5, 1.0],
                        "rows": [0.0, 1.0],
                        "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
                    },
                )

                self._open_file(
                    self.pathbuilder.build_path("test", base_name), 0
                )
                self._open_file(
                    self.pathbuilder.build_path("header", base_name), 1
                ),
                self._open_file(
                    self.pathbuilder.build_path("source", base_name), 1
                ),

            else:
                self._open_file(self.pathbuilder.build_path(option, base_name))

        except IOError as e:
            self.window.status_message("Ceedling: {}".format(e))
            return

    def _open_file(self, file_path, auto_set_view=-1):
        file_view = self.window.open_file(file_path)

        if auto_set_view >= 0:
            self.window.run_command("move_to_group", {"group": auto_set_view})

        self.views.append(file_view)
