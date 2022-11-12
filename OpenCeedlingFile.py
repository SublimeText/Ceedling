import os
import re
import glob

import sublime
import sublime_plugin

from . import CeedlingSettings


class OpenCeedlingFileCommand(sublime_plugin.WindowCommand):
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

        if option == 'config':
            return self.open_file(self.conf.project_yml)

        # Handle files within the project structure
        current_file_path = self.window.active_view().file_name()

        if current_file_path is None:
            return

        filename = re.search(
            r"(?:.+\/|\\)"
            + fr"(?P<prefix>{self.conf.test_file_prefix})?"
            + r"(?P<base>.+?)\."
            + fr"(?P<ext>{self.conf.source_ext}|{self.conf.header_ext})$",
            current_file_path,
        )

        if filename is None:
            self.window.status_message(
                "Ceedling switching: unsupported file type"
            )
            return

        base_name = filename.group("base")

        try:
            if option == 'next':
                if filename.group("prefix"):
                    option = "source"
                elif filename.group("ext") == "c":
                    option = "header"
                else:
                    option = "test"

            if option == 'test_and_source':
                window.run_command(
                    'set_layout',
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
            self.window.status_message(f"Ceedling: {e}")
            return

    def path_build(self, option: str, base: str) -> str:
        # todo: Check this assumption holds when env is set

        ppath = os.path.dirname(self.conf.project_yml)
        ext = self.conf.source_ext

        if option == "test":
            gpath = self.conf.test
            base = "".join((self.conf.test_file_prefix, base))
        elif option == "source":
            gpath = self.conf.source
        else:
            gpath = self.conf.source
            ext = self.conf.header_ext

        res = []

        # use os.path.realpath to clean relative paths
        for glob_pat in gpath:
            p = os.path.realpath(
                os.path.join(ppath, glob_pat, ".".join((base, ext)))
            )
            res.extend(glob.glob(p, recursive=True))

        if len(res) == 0:
            raise IOError("No matching file")

        elif len(res) > 1:
            self.window.status_message(
                "Ceedling: More than one matching file."
            )

            print("Duplicate matches found:")

            for m in res:
                print(m)

        return res[0]

    def open_file(self, file_path, auto_set_view=-1):

        file_view = self.window.open_file(file_path)

        if auto_set_view >= 0:
            self.window.run_command('move_to_group', {'group': auto_set_view})

        self.views.append(file_view)

    def is_enabled(self):
        return self.window.active_view() is not None
