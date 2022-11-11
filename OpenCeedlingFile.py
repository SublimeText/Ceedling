import os
import re
import glob

from . import yaml

from . import CeedlingSettings


class OpenCeedlingFileCommand(WindowCommand):
    def run(self, option):

        self.views = []
        window = self.window

        if not self.window.active_view():
            return

        current_file_path = self.window.active_view().file_name()

        if current_file_path is None:
            return

        self.settings = CeedlingProjectSettings(self.window)

        if option == 'config':
            return self.open_file(self.settings.project_yml)

        filename = re.search(
            r"(?:.+\/|\\)"
            + fr"(?P<prefix>{self.settings.test_file_prefix})?"
            + fr"(?P<base>.+?)\.(?P<ext>c|h)$",
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

            elif option == 'test_and_source':
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

            self.open_file(self.path_build(option, base_name))

        except IOError:
            self.window.status_message("Ceedling: no matching file found")
            return

    def path_build(self, option, base):
        # todo: Check this assumption holds when env is set
        ppath = os.path.dirname(self.settings.project_yml)
        ext = "c"

        if option == "test":
            gpath = self.settings.test
            base = "".join((self.settings.test_file_prefix, base))
        elif option == "source":
            gpath = self.settings.source
        else:
            gpath = self.settings.source
            ext = "h"

        res = []

        # use os.path.realpath to clean relative paths
        for glob_pat in gpath:
            p = os.path.realpath(
                os.path.join(ppath, glob_pat, ".".join((base, ext)))
            )
            res.extend(glob.glob(p, recursive=True))

        if len(res) == 0:
            raise IOError("No matching file")

        return res[0]

    def open_file(self, file_path, auto_set_view=-1):

        file_view = self.window.open_file(file_path)

        if auto_set_view >= 0:
            self.window.run_command('move_to_group', {'group': auto_set_view})

        self.views.append(file_view)

    def is_enabled(self):
        return self.window.active_view() is not None
