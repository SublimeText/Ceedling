import sys

import sublime
import sublime_plugin
from Default.exec import ExecCommand as _ExecCommand

from .CeedlingSettings import CeedlingProjectSettings


class CeedlingExecCommand(_ExecCommand):
    def run(self, **kwargs):

        # "working_dir" is set by "new project" command.
        #  project.xml does not exist unit project is created.
        if kwargs.get("working_dir") is None:
            try:
                self.conf = CeedlingProjectSettings(self.window)

            except OSError as e:
                self.window.status_message("Ceedling: {}".format(e))
                return

            kwargs["working_dir"] = self.conf.working_dir

        variables = self.window.extract_variables()

        # Check if the user is attempting to build an unsupported file.
        if variables.get("file_extension") not in (
            self.conf.source_ext,
            self.conf.header_ext,
        ) and any(i.find("$file") != -1 for i in kwargs.get("tasks")):
            print("File cannot be compiled.")
            return

        task_sub = [
            sublime.expand_variables(task, variables)
            for task in kwargs.pop("tasks", [])
        ]

        # Build up the command line
        if sys.platform == "win32":
            cmd = ["ceedling.bat"]
        else:
            cmd = ["ceedling"]

        for i in (
            kwargs.pop("prefix", []),
            task_sub,
            kwargs.pop("options", []),
        ):
            cmd.extend(i)

        kwargs["cmd"] = cmd

        super().run(**kwargs)
