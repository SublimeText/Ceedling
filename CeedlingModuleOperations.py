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

        # Windows/Linux need folder listing refresh
        sublime.set_timeout_async(
            lambda: window.run_command("refresh_folder_list"), 2000
        )


class CeedlingDestroyModuleCommand(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        variables = self.window.extract_variables()

        if variables.get("file_name") is None:
            sublime.error_message("Nothing to destroy.")
            return None

        try:
            self.conf = CeedlingProjectSettings(self.window)
            self.pathbuilder = CeedlingPathBuilder(self.conf)

        except OSError as e:
            self.window.status_message("Ceedling: %s" % e)
            return

        base_name = self.pathbuilder.split_name(
            variables.get("file_name", "")
        ).get("base")

        if base_name is None:
            sublime.error_message("Cannot destroy selected file.")
            return None

        if sublime.ok_cancel_dialog(
            "Remove all test and source files for {}?".format(base_name),
            ok_title="Destroy",
        ):
            self._destroy(base_name)
        else:
            return None

    def _destroy(self, module_name):
        # Close all target module views without saving
        for i in ("test", "source", "include"):
            f = self.pathbuilder.build_path(i, module_name)
            v = self.window.find_open_file(f)

            if v is not None:
                viewlist = self._find_clones(v)
                viewlist.append(v)
                for vi in viewlist:
                    vi.set_scratch(True)
                    vi.close()

        self.window.run_command(
            "ceedling_exec",
            {"tasks": ["module:destroy[{}]".format(module_name)]},
        )

        # Windows/Linux need folder listing refresh
        sublime.set_timeout_async(
            lambda: window.run_command("refresh_folder_list"), 2000
        )

    def _find_clones(self, view):
        """Return view id of cloned windows."""

        if int(sublime.version()) >= 4080:
            return view.clones()
        else:
            clones = []
            for window in sublime.windows():
                for _view in window.views():
                    if (
                        _view.buffer_id() == view.buffer_id()
                        and view.id() != _view.id()
                    ):
                        clones.append(_view)
            return clones
