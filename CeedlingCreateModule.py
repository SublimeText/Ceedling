import functools

import sublime
import sublime_plugin


class CeedlingCreateModuleCommand(sublime_plugin.WindowCommand):
    def run(self, module=""):

        window = self.window
        view = self.window.active_view()

        window.show_input_panel(
            "Enter new {} name".format(module),
            "",
            functools.partial(self.onDone, view, module),
            None,
            None,
        )

    def onDone(self, view, module, text):
        window = view.window()
        window.status_message("Creating {}: {}".format(module, text ))
        window.run_command("ceedling", {"tasks": ["module:{}[{}]".format(module, text)]})
        window.status_message("Created {}: {}".format(module, text))
