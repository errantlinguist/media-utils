media-utils
===========

A collection of scripts for managing media filesets.

* **Version:** 2014-12-03
* **Author:** Todd Shore
* **Website:** https://github.com/errantlinguist/jtextgrid
* **Licensing:** Copyright &copy; 2011&ndash;2014 Todd Shore. Licensed for distribution under the Apache License 2.0: See the files `NOTICE.txt` and `LICENSE.txt`.

Requirements
--------------------------------------------------------------------------------
- Python 2.7.6+

Contents
--------------------------------------------------------------------------------

* **[remove_empty_dirs.py](https://raw.githubusercontent.com/errantlinguist/media-utils/master/remove_empty_dirs.py):** A script for cleaning up (sub-)directories in a directory tree which do not contain files matching a given content type pattern, e.g. media files such as "*.mp3" or "*.mpg" by default.
* **[set_permissions.sh](https://raw.githubusercontent.com/errantlinguist/media-utils/master/set_permissions.sh):** A script for batch-setting permissions for directories and files, checking each file for a shebang in order to determine if it should have user-set "executable file" permissions applied to it or not.

To do
--------------------------------------------------------------------------------
* Test on Windows systems
