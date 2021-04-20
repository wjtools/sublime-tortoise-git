import sublime
import sublime_plugin
import os
import os.path
import time
import subprocess

git_root_cache = {}


def git_root(directory):
    global git_root_cache

    retval = False
    leaf_dir = directory

    if leaf_dir in git_root_cache and git_root_cache[leaf_dir]['expires'] > time.time():
        return git_root_cache[leaf_dir]['retval']

    while directory:
        if os.path.exists(os.path.join(directory, '.git')):
            retval = directory
            break
        parent = os.path.realpath(os.path.join(directory, os.path.pardir))
        if parent == directory:
            retval = False
            break
        directory = parent

    git_root_cache[leaf_dir] = {
        'retval': retval,
        'expires': time.time() + 5
    }

    return retval


def is_git_controlled(directory):
    return bool(git_root(directory))


def get_setting():
    return sublime.load_settings('TortoiseGit.sublime-settings')


def run_tortoise_git_command(command, args, path, isHung=False):
    settings = get_setting()
    tortoisegit_path = settings.get('tortoisegit_path')

    if tortoisegit_path is None or not os.path.isfile(tortoisegit_path):
        # sublime.error_message('can\'t find TortoiseGitProc.exe, please config setting file\n   --sublime-TortoiseGit')
        # raise
        tortoisegit_path = 'TortoiseGitProc.exe'

    # cmd = '"' + tortoisegit_path + '"' + ' /command:' + cmd + ' /path:"%s"' % dir
    cmd = u'{0} /command:"{1}" /path:"{2}" {3}'.format(
        tortoisegit_path,
        command,
        path,
        u' '.join(args))

    # proce = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        print('Running {0}'.format(cmd))
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(
                cmd,
                stdin=devnull,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=subprocess.SW_HIDE
            )

            # This is required, cause of ST must wait TortoiseGit update then revert
            # the file. Otherwise the file reverting occur before git pull, if the
            # file changed the file content in ST is older.
            if isHung:
                proc.communicate()
    except IOError as ex:
        sublime.error_message('Failed to execute command: {}'.format(str(ex)))
        raise


class TortoiseGitCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return is_git_controlled(self._relevant_path())

    def _active_line_number(self):
        view = self.window.active_view()
        if view:
            row, col = view.rowcol(view.sel()[0].begin())
            return row + 1
        else:
            return None

    def _active_file_path(self):
        view = self.window.active_view()
        if view and view.file_name() and len(view.file_name()) > 0:
            return view.file_name()

    def _active_repo_path(self):
        path = self._active_file_path()
        if not path:
            path = self.window.project_file_name()
        if not path:
            path = self.window.folders()[0]
        if path is None:
            return

        root = git_root(path)

        if root is False:
            return
        else:
            return root

    def _active_file_or_repo_path(self):
        path = self._active_file_path()
        if path is not None:
            return path

        # If no active file, then guess the repo.
        return self._active_repo_path()

    # TODO
    # def _selected_dir(self, dirs):
    #     if len(dirs):
    #         return dirs[0]
    #     else:
    #         return

    def _run_command(self, cmd, paths=[], args=[], isHung=False):
        arguments = []
        line_number = self._active_line_number()
        if line_number:
            # args.append('/line:{}'.format(line_number))
            arguments = args + ['/line:{}'.format(line_number)]

        # TODO
        if len(paths):
            run_tortoise_git_command(cmd, arguments, paths[0])
        else:
            run_tortoise_git_command(cmd, arguments, self._relevant_path())


class GitStatusCommand(TortoiseGitCommand):
    def run(self, paths=[]):
        self._run_command('repostatus', paths)

    def _relevant_path(self):
        return self._active_file_or_repo_path()


class GitLogCommand(TortoiseGitCommand):
    def run(self, paths=[]):
        self._run_command('log', paths)

    def _relevant_path(self):
        return self._active_file_or_repo_path()


class GitDiffCommand(TortoiseGitCommand):
    def run(self, paths=[]):
        self._run_command('diff', paths)

    def _relevant_path(self):
        return self._active_file_or_repo_path()


class GitCommitCommand(TortoiseGitCommand):
    def run(self, paths=[]):
        self._run_command('commit', paths)

    def _relevant_path(self):
        return self._active_file_or_repo_path()


class GitCommitRepoCommand(TortoiseGitCommand):
    def run(self):
        self._run_command('commit')

    def _relevant_path(self):
        return self._active_repo_path()


class GitSyncCommand(TortoiseGitCommand):
    def run(self):
        self._run_command('sync', [], [], True)

    def _relevant_path(self):
        return self._active_repo_path()


class GitBlameCommand(TortoiseGitCommand):
    def run(self):
        self._run_command('blame')

    def _relevant_path(self):
        return self._active_file_path()


class MutatingTortoiseGitCommand(TortoiseGitCommand):
    def run(self, cmd, paths=None, args=[]):
        self._run_command(cmd, paths, args, True)

        self.view = sublime.active_window().active_view()
        row, col = self.view.rowcol(self.view.sel()[0].begin())
        self.lastLine = str(row + 1)
        sublime.set_timeout(self.revert, 100)

    def _relevant_path(self):
        return self._active_file_or_repo_path()

    def revert(self):
        self.view.run_command('revert')
        sublime.set_timeout(self.revertPoint, 600)

    def revertPoint(self):
        self.view.window().run_command('goto_line', {'line': self.lastLine})


class GitPullCommand(MutatingTortoiseGitCommand):
    def run(self, paths=[]):
        settings = get_setting()
        auto_close_dialog = settings.get('auto_close_pull_dialog')
        args = ['/closeonend:2'] if auto_close_dialog else []
        MutatingTortoiseGitCommand.run(self, 'pull', paths, args)


class GitRevertCommand(MutatingTortoiseGitCommand):
    def run(self, paths=[]):
        MutatingTortoiseGitCommand.run(self, 'revert', paths)
