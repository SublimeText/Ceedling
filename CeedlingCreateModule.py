import functools

import sublime_plugin


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
            "ceedling", {"tasks": ["module:{}[{}]".format(module, text)]}
        )
        window.status_message("Created {}: {}".format(module, text))
