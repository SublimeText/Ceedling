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
                "project_dir": project_dir,
            },
        )

        window.status_message("Created project: {}".format(project_name))

        sublime.set_timeout_async(self.open_new_dir(project_name), 1000)

    def get_subl_path(self):
        """Return path to subl executable."""
        platform = sublime.platform()
        version = sublime.version()

        if platform == "osx":
            vers = r"" if version.startswith("4") else r" 3"

            return r"".join(
                [
                    r"/Applications/Sublime Text",
                    vers,
                    r".app/Contents/SharedSupport/bin/subl",
                ]
            )

        elif platform == "linux":
            if os.path.exists(r"/usr/bin/subl"):
                return r"/usr/bin/subl"
            elif os.path.exists(r"/usr/local/bin/subl"):
                return r"/usr/local/bin/subl"

        else:
            if os.path.exists(r"C:\Program Files\Sublime Text"):
                return r"C:\Program Files\Sublime Text\subl.exe"
            else:
                return r"C:\Program Files (x86)\Sublime Text\subl.exe"

        raise IOError("subl binary not found.")

    def open_new_dir(self, folder):
        """Open newly created project in current window."""
        while not (os.path.exists(folder)):
            sleep(0.01)

        os.chdir(folder)
        # Open folder in current Sublime Text window
        subprocess.Popen([self.get_subl_path(), "-a", os.getcwd()])
