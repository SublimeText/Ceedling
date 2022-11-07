import functools
import sublime
import sublime_plugin


class CreateCeedlingModuleCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = self.window.active_view()

        window.show_input_panel(
            "Enter new module name",
            "",
            functools.partial(self.onDone, view),
            None,
            None,
        )

    def onDone(self, view, text):
        window = view.window()
        sublime.status_message("Creating module: " + text)
        window.run_command("rake", {"tasks": ["module:create[" + text + "]"]})
        sublime.status_message("Created module: " + text)
