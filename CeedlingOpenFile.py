import os
import re


import sublime
import sublime_plugin

from . import CeedlingSettings
from . import glob2


class CeedlingOpenFileCommand(sublime_plugin.WindowCommand):
    def run(self, option):

        self.views = []
        window = self.window

        if not self.window.active_view():
            return

        try:
            self.conf = CeedlingSettings.CeedlingProjectSettings(self.window)

        except OSError as e:
            self.window.status_message("Ceedling: %s" % e)
            return

        if option == "config":
            return self.open_file(self.conf.project_yml)

        # Handle files within the project structure
        current_file_path = self.window.active_view().file_name()

        if current_file_path is None:
            return

        _, filename = os.path.split(current_file_path)

        filename = re.search(
            r"(?P<prefix>{})?".format(self.conf.test_file_prefix)
            + r"(?P<base>.+?)\."
            + r"(?P<ext>{}|{})$".format(
                self.conf.source_ext, self.conf.header_ext
            ),
            filename,
        )

        if filename is None:
            self.window.status_message("Ceedling switching: unsupported file")
            return

        base_name = filename.group("base")

        try:
            if option == "next":
                if filename.group("prefix"):
                    option = "source"
                elif filename.group("ext") == "c":
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

                self.open_file(self.path_build("test", base_name), 0)
                self.open_file(self.path_build("source", base_name), 1)
            else:
                self.open_file(self.path_build(option, base_name))

        except IOError as e:
            self.window.status_message("Ceedling: {}".format(e))
            return

    def path_build(self, option: str, base: str) -> str:
        # todo: Check this assumption holds when env is set
        ppath = self.conf.project_dir
        ext = self.conf.source_ext

        if ppath is None:
            raise IOError("missing path")

        if option == "test":
            gpath = self.conf.test
            xpath = self.conf.test_excl

            base = "".join((self.conf.test_file_prefix, base))
        elif option == "source":
            gpath = self.conf.source
            xpath = self.conf.source_excl
        else:
            gpath = self.conf.source
            xpath = self.conf.test_excl
            ext = self.conf.header_ext

        # build list of files based on project.yml glob paths
        incl = self.glob_search(gpath, ppath, base, ext)
        excl = self.glob_search(xpath, ppath, base, ext)

        # remove files from excluded directories from results
        incl = list(set(incl) - set(excl))

        if len(incl) == 0:
            raise IOError("No matching file")

        elif len(incl) > 1:
            self.window.status_message("Ceedling: Multiple matching files.")

            print("Duplicate matches found:")

            for m in incl:
                print(m)

        return incl[0]

    def glob_search(self, pattern, path, base, ext) -> list:
        res = []
        for glob_pat in pattern:

            glob_pat = os.path.normpath(glob_pat)

            p = os.path.abspath(
                os.path.join(path, glob_pat, ".".join((base, ext)))
            )
            res.extend(glob2.glob(p, recursive=True))

        return res

    def open_file(self, file_path, auto_set_view=-1):
        file_view = self.window.open_file(file_path)

        if auto_set_view >= 0:
            self.window.run_command("move_to_group", {"group": auto_set_view})

        self.views.append(file_view)

    def is_enabled(self):
        return self.window.active_view() is not None
