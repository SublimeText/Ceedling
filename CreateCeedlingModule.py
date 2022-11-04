import functools
import sublime
import sublime_plugin

class CreateCeedlingModuleCommand(sublime_plugin.WindowCommand):

	def run(self):
		window = self.window
		view = self.window.active_view()
		current_file_path = view.file_name()
		window.show_input_panel("Enter module path", current_file_path, functools.partial(self.onDone, view), None, None)
	
	def onDone(self, view, text):
		window = view.window()
		sublime.status_message("Creating module: " + text)
		window.run_command("rake", { "tasks": [ "module:create[" + text + "]" ] } )
		sublime.status_message("Created module: " + text)
