import os
import re

from . import yaml


class CeedlingProjectSettings:
    def __init__(self, window):
        self.settings = window.settings()
        self.update_cache(window)

    @property
    def project_yml(self):
        return self._cache_get("project_file")

    @property
    def project_dir(self):
        return self._cache_get("project_dir")

    @property
    def build_root(self):
        return self._cache_get("build_root")

    @property
    def test_file_prefix(self):
        return self._cache_get("test_file_prefix")

    @property
    def test(self) -> list:
        return self._cache_get("test")

    @property
    def test_excl(self) -> list:
        return self._cache_get("test_excl")

    @property
    def source(self) -> list:
        return self._cache_get("source")

    @property
    def source_ext(self) -> list:
        return self._cache_get("source_ext")

    @property
    def header_ext(self) -> list:
        return self._cache_get("header_ext")

    def _cache_set(self, data: dict):
        self.settings.update(data)

    def _cache_get(self, key: str):
        return self.settings.get(key)

    def update_cache(self, window):
        # To use a project file name other than the default project.yml
        # or place the project file in a directory other than the one
        # in which you'll run [ceedling], create an environment variable
        # CEEDLING_MAIN_PROJECT_FILE with your desired project file path.

        if self._cache_get("project_file") is not None:
            project_file = self._cache_get("project_file")

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
        cached_mod = self._cache_get("last_modified")

        if (cached_mod is None) or (last_mod > cached_mod):
            self._cache_set(self.project_file_parse(project_file))
            self._cache_set(
                {"last_modified": last_mod, "project_file": project_file}
            )
            print("Project cache updated")

    def project_file_parse(self, project_file):

        defines = {
            "paths": {
                "source": "src/**",
                "test": "test/**",
                "includes": "src/**",
            },
            "project": {"build_root": "build", "test_file_prefix": "test_"},
            "extension": {"source": "c", "header": "h"},
        }
        config = self.read_yaml(project_file)
        cache_update = {}

        try:
            for section, elements in defines.items():
                for key, default in elements.items():
                    value = config[section].get(key, default)

                    if section == "paths":

                        if isinstance(value, str):
                            value = [value]

                        for i in value:
                            t_key = key

                            if i.startswith(("+")):
                                i = i.lstrip("+")

                            elif i.startswith(("-")):
                                i = i.lstrip("-")

                                if not key.endswith("excl"):
                                    t_key = key + "_excl"

                            t = cache_update.get(t_key, list())
                            t.append(i)
                            cache_update.update({t_key: t})
                    else:
                        if section == "extension":
                            key += "_ext"
                        cache_update.update({key: value})

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
