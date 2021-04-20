# Sublime-TortoiseGit

A TortoiseGit Plugin for [Sublime Text](http://www.sublimetext.com).

## Usage

Install it using [Sublime Package Control](http://wbond.net/sublime_packages/package_control).

The default key bindings:
- [alt+c] : commit current file.
- [alt+u] : update current file.
- [alt+l] : show current file log.

You can also call TortoiseGit commands when right-clicking folders or files in the side bar.

## Settings

If your TortoiseGitProc.exe path is not the default, please modify the path by selecting
"Preferences -> Package Settings -> TortoiseGit -> Settings - User" in the menu.

The default setting is:

```
{
  // Auto close update dialog when no errors, conflicts and merges
  "auto_close_pull_dialog": false,
  "tortoisegit_path": "C:\Program Files\TortoiseGit\bin\TortoiseGitProc.exe"
}
```

## Thanks

Thanks to the authors and contributors of the following repositories,
from whom I got useful direction:

* https://github.com/dexbol/sublime-TortoiseSVN
* https://github.com/fyneworks/sublime-TortoiseGIT
* https://github.com/kemayo/sublime-text-git
* https://github.com/ses4j/tgit-st3
