import collections
import functools
import os
import subprocess
import sys
import threading
import time
import codecs
import signal
import re

import sublime
import sublime_plugin


class ProcessListener(object):
    def on_data(self, proc, data):
        pass

    def on_finished(self, proc):
        pass


class AsyncProcess(object):
    """
    Encapsulates subprocess.Popen, forwarding stdout to a supplied
    ProcessListener (on a separate thread)
    """

    def __init__(self, cmd, env, listener, path="", shell=False):
        """ "path" and "shell" are options in build systems"""

        if not cmd:
            raise ValueError("cmd is required")
        # if cmd and not isinstance(cmd, str):
        # raise ValueError("cmd must be a string")

        self.listener = listener
        self.killed = False

        self.start_time = time.time()

        # Hide the console window on Windows
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Set temporary PATH to locate executable in cmd
        if path:
            old_path = os.environ["PATH"]
            # The user decides in the build system whether he wants to append $PATH
            # or tuck it at the front: "$PATH;C:\\new\\path", "C:\\new\\path;$PATH"
            os.environ["PATH"] = os.path.expandvars(path)

        proc_env = os.environ.copy()
        proc_env.update(env)

        for k, v in proc_env.items():
            proc_env[k] = os.path.expandvars(v)

        if sys.platform == "win32":
            preexec_fn = None
        else:
            preexec_fn = os.setsid

        # Old style build system, just do what it asks
        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            env=proc_env,
            preexec_fn=preexec_fn,
            shell=shell,
        )

        if path:
            os.environ["PATH"] = old_path

        if self.proc.stdout:
            threading.Thread(
                target=self.read_fileno, args=(self.proc.stdout.fileno(), True)
            ).start()

        if self.proc.stderr:
            threading.Thread(
                target=self.read_fileno,
                args=(self.proc.stderr.fileno(), False),
            ).start()

    def kill(self):
        if not self.killed:
            self.killed = True
            if sys.platform == "win32":
                # terminate would not kill process opened by the shell cmd.exe,
                # it will only kill cmd.exe leaving the child running
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen(
                    "taskkill /PID %d /T /F" % self.proc.pid,
                    startupinfo=startupinfo,
                )
            else:
                os.killpg(self.proc.pid, signal.SIGTERM)
                self.proc.terminate()
            self.listener = None

    def poll(self):
        return self.proc.poll() is None

    def exit_code(self):
        return self.proc.poll()

    def read_fileno(self, fileno, execute_finished):
        decoder_cls = codecs.getincrementaldecoder(self.listener.encoding)
        decoder = decoder_cls('replace')
        while True:
            data = decoder.decode(os.read(fileno, 2**16))

            if len(data) > 0:
                if self.listener:
                    self.listener.on_data(self, data)
            else:
                try:
                    os.close(fileno)
                except OSError:
                    pass
                if execute_finished and self.listener:
                    self.listener.on_finished(self)
                break


class CeedlingCommand(sublime_plugin.WindowCommand, ProcessListener):
    BLOCK_SIZE = 2**14
    text_queue = collections.deque()
    text_queue_proc = None
    text_queue_lock = threading.Lock()

    proc = None

    def run(
        self,
        tasks=[],
        options=[],
        prefix=[],
        file_regex="^(...*?):([0-9]*):?([0-9]*)",
        line_regex="",
        working_dir="",
        encoding="utf-8",
        env={},
        quiet=False,
        kill=False,
        # Catches "path" and "shell"
        **kwargs
    ):
        # clear the text_queue
        with self.text_queue_lock:
            self.text_queue.clear()
            self.text_queue_proc = None

        if kill:
            if self.proc:
                self.proc.kill()
                self.proc = None
                self.append_string(None, "[Cancelled]")
            return

        if not hasattr(self, 'output_view'):
            # Try not to call get_output_panel until the regexes are assigned
            self.output_view = self.window.create_output_panel("exec")

        # Search up project structure to locate Ceedling project.yml
        # Ceedling must run from same directory as project file.

        if os.getenv('CEEDLING_MAIN_PROJECT_FILE') is None:
            file_list = [
                (folder, file)
                for folder in self.window.folders()
                for file in ["project.yml", "test.yml"]
            ]

            for folder, file in file_list:
                project_file = os.path.join(folder, file)
                if os.path.isfile(project_file):
                    project_dir = folder
                    break
            else:
                raise ValueError(
                    "project.yml not found in project root folder."
                )

        self.output_view.settings().set("result_file_regex", file_regex)
        self.output_view.settings().set("result_line_regex", line_regex)
        self.output_view.settings().set("result_base_dir", project_dir)
        self.output_view.settings().set("line_numbers", False)
        self.output_view.settings().set("gutter", False)
        self.output_view.settings().set("scroll_past_end", False)

        # Ceedling Specific
        current_file = self.window.active_view().file_name()
        current_file_name = os.path.basename(current_file)
        current_dir = project_dir

        flattened_tasks = ""

        for task in tasks:
            task = task.replace("$file_name", current_file_name)
            task = task.replace("$file", current_file)
            flattened_tasks += task + " "

        flattened_tasks = re.sub(r" $", "", flattened_tasks)

        # Build up the command line
        cmd = []
        cmd += prefix

        if sys.platform == "win32":
            cmd += ["ceedling.bat"]
        else:
            cmd += ["ceedling"]

        cmd += [flattened_tasks] + options

        # Call create_output_panel a second time after assigning the above
        # settings, so that it'll be picked up as a result buffer
        self.window.create_output_panel("exec")

        self.encoding = encoding
        self.quiet = quiet
        self.proc = None

        self.append_string(None, "> " + " ".join(cmd) + "\n")
        self.window.run_command("show_panel", {"panel": "output.exec"})

        merged_env = env.copy()
        if self.window.active_view():
            user_env = self.window.active_view().settings().get('build_env')
            if user_env:
                merged_env.update(user_env)

        # Change to the working dir, rather than spawning the process with it,
        # so that emitted working dir relative path names make sense
        if current_dir != "":
            os.chdir(current_dir)

        self.debug_text = ""
        self.debug_text += "[cmd: " + str(cmd) + "]\n"
        self.debug_text += "[dir: " + str(os.getcwd()) + "]\n"

        if "PATH" in merged_env:
            self.debug_text += "[path: " + str(merged_env["PATH"]) + "]"
        else:
            self.debug_text += "[path: " + str(os.environ["PATH"]) + "]"

        try:
            # Forward kwargs to AsyncProcess
            self.proc = AsyncProcess(cmd, merged_env, self, **kwargs)

            with self.text_queue_lock:
                self.text_queue_proc = self.proc

        except Exception as e:
            self.append_string(None, str(e) + "\n")
            self.append_string(None, self.debug_text + "\n")
            if not self.quiet:
                self.append_string(None, "[Finished]")

    def is_enabled(self, kill=False, **kwargs):
        if kill:
            return (self.proc is not None) and self.proc.poll()
        else:
            return True

    def append_string(self, proc, str):
        was_empty = False
        with self.text_queue_lock:
            if proc != self.text_queue_proc and proc:
                # a second call to exec has been made before the first one
                # finished, ignore it instead of intermingling the output.
                proc.kill()
                return

            if len(self.text_queue) == 0:
                was_empty = True
                self.text_queue.append("")

            available = self.BLOCK_SIZE - len(self.text_queue[-1])

            if len(str) < available:
                cur = self.text_queue.pop()
                self.text_queue.append(cur + str)
            else:
                self.text_queue.append(str)

        if was_empty:
            sublime.set_timeout(self.service_text_queue, 0)

    def service_text_queue(self):
        is_empty = False
        with self.text_queue_lock:
            if len(self.text_queue) == 0:
                # this can happen if a new build was started, which will clear
                # the text_queue
                return

            characters = self.text_queue.popleft()
            is_empty = len(self.text_queue) == 0

        self.output_view.run_command(
            'append',
            {'characters': characters, 'force': True, 'scroll_to_end': True},
        )

        if not is_empty:
            sublime.set_timeout_async(self.service_text_queue, 1)

    def finish(self, proc):
        if not self.quiet:
            elapsed = time.time() - proc.start_time
            exit_code = proc.exit_code()
            if exit_code == 0 or exit_code is None:
                self.append_string(proc, "[Finished in %.1fs]" % elapsed)
            else:
                self.append_string(
                    proc,
                    "[Finished in %.1fs with exit code %d]\n"
                    % (elapsed, exit_code),
                )
                self.append_string(proc, self.debug_text)

        if proc != self.proc:
            return

        errs = self.output_view.find_all_results()
        if len(errs) == 0:
            sublime.status_message("Build finished")
        else:
            sublime.status_message("Build finished with %d errors" % len(errs))

    def on_data(self, proc, data):
        # Normalize newlines, Sublime Text always uses a single \n separator
        # in memory.
        data = data.replace('\r\n', '\n').replace('\r', '\n')

        self.append_string(proc, data)

    def on_finished(self, proc):
        sublime.set_timeout(functools.partial(self.finish, proc), 0)
