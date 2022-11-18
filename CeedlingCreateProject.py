import functools
import os
import sublime
import sublime_plugin
import subprocess
from time import sleep


class CeedlingCreateProjectCommand(sublime_plugin.WindowCommand):
    def run(self, options=[]):

        window = self.window
        view = self.window.active_view()

        # stash project options
        self.options = options
        # print((self.window.settings().to_dict()))
        plugin_settings = sublime.load_settings("Ceedling.sublime-settings")
        self.default_parent = os.path.normpath(
            plugin_settings.get("default_project_folder")
        )
        window.show_input_panel(
            "Enter new project path: ",
            self.default_parent,
            functools.partial(self.on_done, view),
            None,
            None,
        )

    def on_done(self, view, path):
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
                "options": self.options,
                "project_dir": project_dir,
            },
        )
        window.status_message("Created project: {}".format(project_name))
        sublime.set_timeout_async(self.open_new_dir(project_name), 1000)

    def get_cli_path(self):
        """Return path to subl executable."""
        platform = sublime.platform()
        version = sublime.version()

        if platform == "osx":
            if version.startswith("4"):
                return r"/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl"
            else:
                return r"/Applications/Sublime Text 3.app/Contents/SharedSupport/bin/subl"

        elif platform == "linux":
            if os.path.exists(r"/usr/bin/subl"):
                return r"/usr/bin/subl"
            elif os.path.exists(r"/usr/local/bin/subl"):
                return r"/usr/local/bin/subl"
            else:
                raise IOError("Sublime Text cli binary not found")
        else:
            if os.path.exists(r"C:\Program Files\Sublime Text"):
                p = r"C:\Program Files\Sublime Text"
            else:
                p = r"C:\Program Files (x86)\Sublime Text"
            return os.path.join(p, "subl.exe")

        raise IOError("Sublime Text cli binary not found.")

    def open_new_dir(self, folder):
        """Open newly created project in current window."""
        while not (os.path.exists(folder)):
            sleep(0.01)

        os.chdir(folder)
        # Open folder in current Sublime Text window
        subprocess.Popen([self.get_cli_path(), "-a", os.getcwd()])
