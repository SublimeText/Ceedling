import functools

import sublime
import sublime_plugin

from .CeedlingOpenFile import CeedlingPathBuilder
from .CeedlingSettings import CeedlingProjectSettings


class CeedlingCreateModuleCommand(sublime_plugin.WindowCommand):
    def run(self, action="create"):

        window = self.window
        view = self.window.active_view()

        if action == "create":
            desc = "Module"
        elif action == "stub":
            desc = "Stub"
        else:
            return

        window.show_input_panel(
            "Enter new {} name".format(desc),
            "",
            functools.partial(self.on_done, view, action),
            None,
            None,
        )

    def on_done(self, view, module, text):
        """Handler for onDone event."""
        window = view.window()
        window.status_message("Creating {}: {}".format(module, text))
        window.run_command(
            "ceedling_exec", {"tasks": ["module:{}[{}]".format(module, text)]}
        )
        window.status_message("Created {}: {}".format(module, text))


class CeedlingDestroyModuleCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        variables = self.window.extract_variables()

        if variables.get("file_name") is None:
            sublime.error_message("Cannot destroy nothing.")
            return None

        try:
            self.conf = CeedlingProjectSettings(self.window)
            self.pathbuilder = CeedlingPathBuilder(self.conf)
        except OSError as e:
            self.window.status_message("Ceedling: %s" % e)
            return

        name_parts = self.pathbuilder.split_name(
            variables.get("file_name", "")
        )

        if name_parts is None or name_parts.get("base") is None:
            sublime.error_message("Cannot destroy current selection")
            return None

        if sublime.ok_cancel_dialog(
            "Remove all test and source files for {}?".format(
                name_parts.get("base")
            ),
            ok_title="Destroy",
            title="Destroying module",
        ):
            self._destroy(name_parts.get("base"))
        else:
            return None

    def _destroy(self, module_name):
        # Close all target module views without saving
        for i in ("test", "source", "include"):
            f = self.pathbuilder.build_path(i, module_name)
            v = self.window.find_open_file(f)
            if v is not None:
                viewlist = v.clones()
                viewlist.append(v)
                for vi in viewlist:
                    vi.set_scratch(True)
                    vi.close()

        self.window.run_command(
            "ceedling_exec",
            {"tasks": ["module:destroy[{}]".format(module_name)]},
        )
