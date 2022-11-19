import os
import subprocess
import sys
import threading
import time
import codecs
import signal


import sublime
import sublime_plugin

from .CeedlingSettings import CeedlingProjectSettings


class ProcessListener(object):
    def on_data(self, proc, data):
        pass

    def on_finished(self, proc):
        pass


class AsyncProcess(object):
    """
    Encapsulates subprocess.Popen, forwarding stdout to a supplied.
    ProcessListener (on a separate thread)
    """

    def __init__(self, cmd, env, listener, path="", shell=False):
        """ "path" and "shell" are options in build systems."""

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
            # The user decides in the build system
            # whether they want to append $PATH
            # or tuck it at the front:
            # "$PATH;C:\\new\\path", "C:\\new\\path;$PATH"
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
            bufsize=0,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=startupinfo,
            env=proc_env,
            preexec_fn=preexec_fn,
            shell=shell,
        )

        if path:
            os.environ["PATH"] = old_path

        self.stdout_thread = threading.Thread(
            target=self.read_fileno, args=(self.proc.stdout, True)
        )

    def start(self):
        self.stdout_thread.start()

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

    def read_fileno(self, file, execute_finished):
        decoder = codecs.getincrementaldecoder(self.listener.encoding)(
            "replace"
        )

        while True:
            data = decoder.decode(file.read(2**16))
            data = data.replace("\r\n", "\n").replace("\r", "\n")

            if len(data) > 0 and not self.killed:
                self.listener.on_data(self, data)
            else:
                if execute_finished:
                    self.listener.on_finished(self)
                break


class CeedlingCommand(sublime_plugin.WindowCommand, ProcessListener):
    OUTPUT_LIMIT = 2**27

    def __init__(self, window):
        super().__init__(window)
        self.proc = None
        self.errs_by_file = {}
        self.output_view = None

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
        kill_previous=False,
        syntax="Packages/Text/Plain text.tmLanguage",
        # Catches "path" and "shell"
        **kwargs
    ):

        if kill:
            if self.proc:
                self.proc.kill()
            return

        if kill_previous and self.proc and self.proc.poll():
            self.proc.kill()

        if self.output_view is None:
            # Try not to call get_output_panel until the regexes are assigned
            self.output_view = self.window.create_output_panel("exec")

        # "working_dir" is set by "new project" command.
        #  project.xml does not exist unit project is created.
        if not working_dir:
            try:
                self.conf = CeedlingProjectSettings(self.window)

            except OSError as e:
                self.window.status_message("Ceedling: {}".format(e))
                return

            working_dir = self.conf.working_dir

        self.output_view.settings().set("result_file_regex", file_regex)
        self.output_view.settings().set("result_line_regex", line_regex)
        self.output_view.settings().set("result_base_dir", working_dir)

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

        for t in tasks:
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

        for i in (prefix, task_sub, options):
            cmd.extend(i)

        # Call create_output_panel a second time after assigning the above
        # settings, so that it'll be picked up as a result buffer

        self.window.create_output_panel("exec")

        self.encoding = encoding
        self.quiet = quiet
        self.proc = None

        self.write("> " + " ".join(cmd) + "\n")
        self.window.run_command("show_panel", {"panel": "output.exec"})

        merged_env = env.copy()
        if self.window.active_view():
            user_env = self.window.active_view().settings().get("build_env")
            if user_env:
                merged_env.update(user_env)

        # Change to the working dir, rather than spawning the process with it,
        # so that emitted working dir relative path names make sense
        if working_dir != "":
            os.chdir(working_dir)

        self.debug_text = ""
        self.debug_text += "[cmd: " + str(cmd) + "]\n"
        self.debug_text += "[dir: " + str(os.getcwd()) + "]\n"

        if "PATH" in merged_env:
            self.debug_text += "[path: " + str(merged_env["PATH"]) + "]"
        else:
            self.debug_text += "[path: " + str(os.environ["PATH"]) + "]"

        self.output_size = 0
        self.should_update_annotations = False

        try:
            # Forward kwargs to AsyncProcess
            self.proc = AsyncProcess(cmd, merged_env, self, **kwargs)

            self.proc.start()

        except Exception as e:
            self.write(str(e) + "\n")
            self.write(self.debug_text + "\n")
            if not self.quiet:
                self.write("[Finished]")

    def is_enabled(self, kill=False, **kwargs):
        if kill:
            return (self.proc is not None) and self.proc.poll()
        else:
            return True

    def write(self, characters):
        self.output_view.run_command(
            "append",
            {"characters": characters, "force": True, "scroll_to_end": True},
        )

    def on_finished(self, proc):
        if proc != self.proc:
            return

        if proc.killed:
            self.write("\n[Cancelled]")

        elif not self.quiet:
            elapsed = time.time() - proc.start_time
            if elapsed < 1:
                elapsed_str = "%.0fms" % (elapsed * 1000)
            else:
                elapsed_str = "%.1fs" % (elapsed)

            exit_code = proc.exit_code()
            if exit_code == 0 or exit_code is None:
                self.write("[Finished in %s]" % elapsed_str)
            else:
                self.write(
                    "[Finished in %s with exit code %d]\n"
                    % (elapsed_str, exit_code)
                )
                self.write(self.debug_text)

        if proc.killed:
            sublime.status_message("Build cancelled")
        else:
            errs = self.output_view.find_all_results()
            if len(errs) == 0:
                sublime.status_message("Build finished")
            else:
                sublime.status_message(
                    "Build finished with %d errors" % len(errs)
                )

    def on_data(self, proc, data):
        if proc != self.proc:
            return

        # Truncate past the limit
        if self.output_size >= self.OUTPUT_LIMIT:
            return

        self.write(data)
        self.output_size += len(data)

        if self.output_size >= self.OUTPUT_LIMIT:
            self.write("\n[Output Truncated]\n")
