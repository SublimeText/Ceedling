import os
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

        current_file = self.window.active_view().file_name()

        if current_file is None:
            current_file = current_file_name = ""

        else:
            _, current_ext = os.path.splitext(current_file)
            if current_ext in ("", ".yml", ".rb"):
                return

            else:
                current_file_name = os.path.basename(current_file)

        task_sub = []

        for t in kwargs.pop("tasks"):
            for p, v in zip(
                ["$file_name", "$file"],
                [current_file_name, current_file],
            ):
                # verify tasks with a placeholder have a replacement value
                if t.rfind(p) >= 0 and v == "":
                    return

                t = t.replace(p, v)

            task_sub.append(t)

        # Build up the command line
        if sys.platform == "win32":
            cmd = ["ceedling.bat"]
        else:
            cmd = ["ceedling"]

        prefix = kwargs.pop("prefix", [])
        options = kwargs.pop("options", [])

        for i in (prefix, task_sub, options):
            cmd.extend(i)

        kwargs["cmd"] = cmd

        super().run(**kwargs)
