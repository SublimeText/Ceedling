import os
import re

import yaml
import sublime
import sublime_plugin


class CeedlingUserSettings:
    _settings = {}

    def __init__(self):
        self._settings = sublime.load_settings("Ceedling.sublime-settings")

    def _write_settings(self):
        sublime.save_settings("Ceedling.sublime-settings")

    @property
    def default_folder(self):
        return os.path.normpath(
            self._settings.get("default_project_folder", "~")
        )

    @property
    def project_options(self):
        return self._settings.get("project_options", "")

    @property
    def logging(self):
        return self._settings.get("logging", False)

    def toggle_logging(self):
        self._settings.set("logging", not self.logging)
        self._write_settings()

    @property
    def verbose(self):
        return self._settings.get("verbose", False)

    @property
    def verbose_level(self):
        return self._settings.get("verbose_level", 0)

    def toggle_verbose(self):
        self._settings.set("verbose", not self.verbose)
        self._write_settings()


class CeedlingSettingsCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        cmd = kwargs.get("cmd")

        if cmd is None:
            return

        settings = CeedlingUserSettings()

        if cmd == "toggle_logging":
            settings.toggle_logging()

        elif cmd == "toggle_verbose":
            settings.toggle_verbose()


class CeedlingProjectSettings:
    """project.yml configuration parser."""

    def __init__(self, window):
        """Initialise and update settings cache."""
        self.settings = window.settings()
        self._cache_update(window)

    @property
    def project_yml(self):
        """Return path to project.yml."""
        return self._cache_get("project_file")

    @property
    def working_dir(self):
        """Return path to project directory."""
        return self._cache_get("working_dir")

    @property
    def build_root(self):
        """Return build folder path."""
        return self._cache_get("build_root")

    @property
    def test_file_prefix(self):
        """Return prefix for test files."""
        return self._cache_get("test_file_prefix")

    @property
    def test(self):
        """Return glob path to test directories."""
        return self._cache_get("test")

    @property
    def test_excl(self):
        """Return glob path to excluded test directories."""
        return self._cache_get("test_excl", [])

    @property
    def source(self):
        """Return source paths."""
        return self._cache_get("source")

    @property
    def source_excl(self):
        """Return paths excluded from source search."""
        return self._cache_get("source_excl", [])

    @property
    def includes(self):
        """Return includes paths if configured."""
        return self._cache_get("includes", self._cache_get("source"))

    @property
    def includes_excl(self):
        """Return excluded include paths, if configured."""
        return self._cache_get(
            "includes_excl", self._cache_get("includes_excl", [])
        )

    @property
    def source_ext(self):
        """Return configured source file extension."""
        return self._cache_get("source_ext")

    @property
    def header_ext(self):
        """Return configured header file extension."""
        return self._cache_get("header_ext")

    @property
    def release_build(self):
        """Return configured header file extension."""
        return self._cache_get("release_build")

    def _cache_set(self, data):
        for k, v in data.items():
            self.settings.set(k, v)

    def _cache_get(self, key, default=None):
        c = self.settings.get(key, default)
        return c if c is not None else default

    def _cache_update(self, window):
        """
        Locate configuration based on Ceedling documentation.

        To use a project file name other than the default project.yml
        or place the project file in a directory other than the one
        in which you'll run [ceedling], create an environment variable
        CEEDLING_MAIN_PROJECT_FILE with your desired project file path.
        """
        if os.path.exists(self._cache_get("project_yml", default="")):
            project_file = self.project_yml

        elif os.getenv("CEEDLING_MAIN_PROJECT_FILE") is not None:
            project_file = os.getenv("CEEDLING_MAIN_PROJECT_FILE")

        else:
            for folder in window.folders():
                project_file = os.path.join(folder, "project.yml")
                if os.path.isfile(project_file):
                    break
            else:
                raise IOError("Configuration file 'project.yml' not found.")

        # Update if cache is out of date or doesn't exist
        project_timestamp = os.stat(project_file).st_mtime
        cached_timestamp = self._cache_get("last_modified")

        if (cached_timestamp is None) or (
            project_timestamp > cached_timestamp
        ):
            self._cache_set(self._project_file_parse(project_file))
            self._cache_set(
                {
                    "last_modified": project_timestamp,
                    "project_file": project_file,
                    "working_dir": os.path.dirname(project_file),
                }
            )
            print("Project cache updated")

    def _project_file_parse(self, project_file):
        """Return project settings.

        parameter: project_file - path to project.yml
        extract paths, build_root, test prefix and file extensions.
        """
        yml_default = {
            "paths": {
                "source": "src/**",
                "test": "test/**",
                "includes": None,
            },
            "project": {
                "build_root": "build",
                "test_file_prefix": "test_",
                "release_build": False,
            },
            "extension": {"source": "c", "header": "h"},
        }

        config = self._read_yaml(project_file)
        project_settings = {}

        try:
            for section, elements in yml_default.items():
                for key, default in elements.items():
                    value = config[section].get(key, default)

                    if section == "paths":
                        # optional include path is None by default
                        if value is None:
                            project_settings.update({key: value})
                            continue

                        # value is a bare string
                        if isinstance(value, str):
                            value = [value]

                        # value is a list of glob expressions
                        for i in value:
                            t_key = key

                            if i.startswith(("+")):
                                i = i.lstrip("+")

                            elif i.startswith(("-")):
                                i = i.lstrip("-")

                                if not key.endswith("excl"):
                                    t_key = key + "_excl"

                            t = project_settings.get(t_key, list())
                            t.append(i)
                            project_settings.update({t_key: t})
                    else:
                        if section == "extension":
                            key += "_ext"
                        project_settings.update({key: value})

        except KeyError as e:
            print("Key missing:\n", e)
            raise KeyError(e)

        return project_settings

    def _read_yaml(self, project_file):
        """Read project.yml configuration file.

        parameters: project_file - path to project.yml
        """
        with open(project_file, "r") as f:
            pf = f.read()

        # strip Ruby leading colons
        pf = re.sub(r":([a-z])", r"\1", pf)
        pf = re.sub(r"([+-]):", r"\1", pf)

        return yaml.load(pf, Loader=yaml.SafeLoader)
