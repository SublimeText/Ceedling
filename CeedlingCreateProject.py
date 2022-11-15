import functools
import sys
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
        self.default_parent = plugin_settings.get("default_project_folder")
        window.show_input_panel(
            "Enter new project path: ",
            self.default_parent,
            functools.partial(self.onDone, view),
            None,
            None,
        )

    def onDone(self, view, path):
        pfolder = os.path.abspath(os.path.expanduser(path))
        project_dir, project_name = os.path.split(pfolder)

        # Catch mistyped path
        if not os.path.isdir(project_dir):
            sublime.error_message("Parent folder does not exist.\n")
            return

        # User hit enter without entering a path
        if path in (self.default_parent, self.default_parent + "/"):
            sublime.error_message(f"Project name not supplied: {pfolder}\n")
            return

        # Check project directory exists and is writeable
        if not os.access(project_dir, os.W_OK):
            sublime.error_message(
                f"Project location not writeable: {project_dir}\n"
            )
            return

        window = view.window()
        window.status_message(f"Creating project: {project_name}")
        window.run_command(
            "ceedling",
            {
                "tasks": ["new", f"{project_name}"],
                "options": self.options,
                "project_dir": project_dir,
            },
        )

        window.status_message(f"Created project: {project_name}")
        sublime.set_timeout_async(self.open_new_dir(project_name), 1000)

    def get_cli_path(self):
        # Logic taken from:
        # https://github.com/al63/SublimeFiles/blob/master/sublime_files.py

        platform = sublime.platform()

        if platform == "osx":
            return '/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl'
        elif platform == "linux":
            return (
                open('/proc/' + str(os.getppid()) + '/cmdline')
                .read()
                .split(chr(0))[0]
            )
        else:
            return os.path.join(sys.path[0], 'sublime_text.exe')

    def open_new_dir(self, folder):
        # give ceedling time to build directory structure
        while not (os.path.exists(folder)):
            sleep(0.005)

        # Change cwd to the new directory
        _, f = os.path.split(folder)
        os.chdir(f)

        # open folder in current window
        subprocess.Popen([self.get_cli_path(), "-a", os.getcwd()])
