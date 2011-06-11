import sublime
import sublime_plugin
import re, inspect, os

class OpenCeedlingFileCommand(sublime_plugin.WindowCommand):

	def run(self, option):
		if not self.window.active_view():
			return

		self.views = []
		window = self.window
		current_file_path = self.window.active_view().file_name()
		
		if option == 'config':
			config_matcher = re.compile(r"(\\\\)?(project|test)\.yml$")
			self.open_project_file(config_matcher, self.window)
		
		elif re.search(r"\w+\.[ch]\w*$", current_file_path):
			
			current_file = re.search(r"([\w\.]+)$", current_file_path).group(1)
			base_name = re.search(r"(\w+)\.(\w+)$", current_file).group(1)
			base_name = re.sub('^test_', '', base_name)

			print "Basename: " + base_name
			
			source_matcher = re.compile(base_name + "\.c$")
			header_matcher = re.compile(base_name + "\.h$")
			test_matcher   = re.compile("test_" + base_name + "\.c$")
			
			if option == 'next':
				if re.match("test_", current_file):
					self.open_project_file(source_matcher, window)
				elif re.search(r"\.c", current_file):
					self.open_project_file(header_matcher, window)
				elif re.search(r"\.h", current_file):
					self.open_project_file(test_matcher, window)
			elif option == 'source':
				self.open_project_file(source_matcher, window)
			elif option == 'test':
				self.open_project_file(test_matcher, window)
			elif option == 'header':
				self.open_project_file(header_matcher, window)
			elif option == 'test_and_source':
				window.run_command('set_layout', {
                            "cols": [0.0, 0.5, 1.0],
                            "rows": [0.0, 1.0],
                            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                        })
				self.open_project_file(test_matcher, window, 0)
				self.open_project_file(source_matcher, window, 1)
			
		# for v in self.views:
			# window.focusView(v)
		
		# for m in inspect.getmembers(window):
		# 	print m
		# print "-------------------------------------"
		# print window.active_view().file_name()
		# print window.active_group()
				
	def open_project_file(self, file_matcher, window, auto_set_view=-1):
		for root, dirs, files in os.walk(window.folders()[0]):
			for f in files:
				if file_matcher.search(f):
					# if auto_set_view >= 0: # don't set the view unless specified
						# print "=============================="
						# window.focus_group(auto_set_view)
						# print "Set focus to: "
						# print auto_set_view
						# print "=============================="
					file_view = window.open_file(os.path.join(root, f))
					if auto_set_view >= 0: # don't set the view unless specified
						window.run_command('move_to_group', {'group': auto_set_view})
					self.views.append(file_view)
					print("Opened: " + f)
					return
				# else:
				# 	print("No match: " + f)
			# for d in dirs:
				# print("Dir: " + d)
		print("No matching files!")
