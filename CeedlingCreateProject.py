import functools
import os
import sublime
import sublime_plugin
from .CeedlingSettings import CeedlingUserSettings

# Taken from:
# https://github.com/SublimeText/PackageDev/blob/master/plugins/create_package.py#L47
def open_new_window():
    sublime.run_command("new_window")
    return sublime.active_window()


class CeedlingCreateProjectCommand(sublime_plugin.WindowCommand):
    """Create new Ceedling project directory."""

    def run(self, options=[]):

        window = open_new_window()
        view = window.active_view()

        user_settings = CeedlingUserSettings()

        self.default_parent = user_settings.default_folder

        options.extend(user_settings.project_options)

        # Remove any duplicate options
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
            "ceedling_exec",
            {
                "tasks": ["new", "{}".format(project_name)],
                "options": options,
                "working_dir": project_dir,
            },
        )

        window.status_message("Created project: {}".format(project_name))

        sublime.active_window().set_project_data(
            {
                "folders": [
                    {
                        "name": project_name,
                        "path": path,
                        "binary_file_patterns": [
                            "*.o",
                            "*.elf",
                            "*.hex",
                            "*.out",
                        ],
                        "index_exclude_patterns": [
                            "build/artifacts/*",
                            "build/gcov/*",
                            "build/logs/*",
                            "build/temp/*",
                            "build/test/*",
                            "ceedling",
                            "docs/CMock*.md",
                            "docs/Ceedling*.md",
                            "docs/ThrowTheSwitch*.md",
                            "docs/Unity*.md",
                            "docs/plugin_*.md",
                            "project.yml",
                            "test/simulation/*",
                            "vendor/ceedling/*",
                        ],
                    }
                ]
            }
        )

        # Windows/Linux need folder listing refresh
        sublime.set_timeout_async(
            lambda: window.run_command("refresh_folder_list"), 3500
        )
