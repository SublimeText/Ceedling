import functools

import sublime
import sublime_plugin


class CreateCeedlingModuleCommand(sublime_plugin.WindowCommand):
    def run(self, module=""):

        window = self.window
        view = self.window.active_view()

        window.show_input_panel(
            f"Enter new {module} name",
            "",
            functools.partial(self.onDone, view, module),
            None,
            None,
        )

    def onDone(self, view, module, text):
        window = view.window()
        window.status_message(f"Creating {module}: {text}")
        window.run_command("ceedling", {"tasks": [f"module:{module}[{text}]"]})
        window.status_message(f"Created {module}: {text}")
