import functools
import os
import sublime
import sublime_plugin
import subprocess
from time import sleep


class CeedlingCreateProjectCommand(sublime_plugin.WindowCommand):
    """Create new Ceedling project directory."""

    def run(self, options=[]):

        window = self.window
        view = self.window.active_view()

        plugin_settings = sublime.load_settings("Ceedling.sublime-settings")

        self.default_parent = os.path.normpath(
            plugin_settings.get("default_project_folder")
        )

        options.extend(plugin_settings.get("project_options", ""))

        # Remove duplicates
        options = list(set(options))

        window.show_input_panel(
            "Enter new project path: ",
            self.default_parent,
            functools.partial(self.on_done, view, options),
            None,
            None,
        )

    def on_done(self, view, options, path):
        """Handler for onDone event."""
        path = os.path.normpath(path)
        pfolder = os.path.abspath(os.path.expanduser(path))
        project_dir, project_name = os.path.split(pfolder)

        # Catch mistyped path
        if not os.path.isdir(project_dir):
            sublime.error_message("Parent folder does not exist.\n")
            return

        # User hit enter without entering a path
        if path in (self.default_parent, self.default_parent + "/"):
            sublime.error_message(
                "Project name not supplied: {}\n".format(pfolder)
            )
            return

        # Check project directory exists and is writeable
        if not os.access(project_dir, os.W_OK):
            sublime.error_message(
                "Project location not writeable: {}\n".format(project_dir)
            )
            return

        window = view.window()
        window.status_message("Creating project: {}".format(project_name))
        window.run_command(
            "ceedling",
            {
                "tasks": ["new", "{}".format(project_name)],
                "options": options,
                "working_dir": project_dir,
            },
        )

        window.status_message("Created project: {}".format(project_name))

        sublime.active_window().set_project_data(
            {"folders": [{"name": project_name, "path": path}]}
        )
