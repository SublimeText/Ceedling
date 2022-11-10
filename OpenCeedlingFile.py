import os
import re
import glob

from . import yaml

from sublime_plugin import WindowCommand


class CeedlingProjectSettings:
    cache = {}

    def __init__(self, window):
        self.update_cache(window)

    @property
    def project_yml(self):
        return self.cache_get("project_file")

    @property
    def build_root(self):
        return self.cache_get("build_root")

    @property
    def test_file_prefix(self):
        return self.cache_get("test_file_prefix")

    @property
    def test(self) -> list:
        return self.cache_get("test")

    @property
    def test_excl(self) -> list:
        return self.cache_get("test_excl")

    @property
    def source(self) -> list:
        return self.cache_get("source")

    def _cache_set(self, data: dict):
        self.cache.update(data)

    def cache_get(self, key: str):
        return self.cache.get(key)

    def update_cache(self, window):
        # To use a project file name other than the default project.yml
        # or place the project file in a directory other than the one
        # in which you'll run [ceedling], create an environment variable
        # CEEDLING_MAIN_PROJECT_FILE with your desired project file path.

        if self.cache_get("project_file") is not None:
            project_file = self.cache_get("project_file")

        elif os.getenv('CEEDLING_MAIN_PROJECT_FILE') is not None:
            project_file = os.getenv('CEEDLING_MAIN_PROJECT_FILE')

        else:
            for folder in window.folders():
                project_file = os.path.join(folder, "project.yml")
                if os.path.isfile(project_file):
                    break
            else:
                raise IOError("Configuration file 'project.yml' not found.")

        last_mod = os.stat(project_file).st_mtime
        cached_mod = self.cache_get("last_modified")

        if (cached_mod is None) or (last_mod > cached_mod):
            self._cache_set(self.project_file_parse(project_file))
            self._cache_set(
                {"last_modified": last_mod, "project_file": project_file}
            )
            print("Project cache updated")

    def project_file_parse(self, project_file):

        paths = {"source": "src/", "test": "test/", "includes": "src/"}
        project = {"build_root": "build/", "test_file_prefix": "test_"}

        config = self.read_yaml(project_file)

        try:
            cache_update = {
                k: f'{config["project"].get(k, d)}' for k, d in project.items()
            }

            for param, default in paths.items():
                for param_item in config["paths"].get(param, default):
                    print(param_item)

                    if param_item.startswith(("+")):
                        param_item = param_item.lstrip("+")

                    elif param_item.startswith(("-")):
                        param_item = param_item.lstrip("-")

                        if not param.endswith("excl"):
                            param += "_excl"

                    t = cache_update.get(param, list())
                    t.append(param_item)

                    cache_update.update({param: t})

        except KeyError as e:
            print("Key missing:\n", e)
            raise KeyError(e)

        return cache_update

    def read_yaml(self, project_file):
        # project.yml uses keys defined as ruby objects with leading colon.
        with open(project_file, 'r') as f:
            pf = f.read()

        # strip leading colons
        pf = re.sub(r":([a-z])", r"\1", pf)

        return yaml.load(pf, Loader=yaml.FullLoader)


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
        print(self.settings.source, base)
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

        for glob_pat in gpath:
            p = os.path.realpath(
                os.path.join(ppath, glob_pat, ".".join((base, ext)))
            )
            res.extend(glob.glob(p, recursive=True))

        if len(res) == 0:
            raise IOError("No matching file")
        print(res)
        return res[0]

    def open_file(self, file_path, auto_set_view=-1):

        file_view = self.window.open_file(file_path)

        if auto_set_view >= 0:
            self.window.run_command('move_to_group', {'group': auto_set_view})

        self.views.append(file_view)

    def is_enabled(self):
        return self.window.active_view() is not None
