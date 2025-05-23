# A simple (and fast) requirements.txt file generator

[![PyPI - Version](https://img.shields.io/pypi/v/preqs?style=flat-square)](https://pypi.org/project/preqs)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/preqs?style=flat-square)](https://pypi.org/project/preqs)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/preqs?style=flat-square)](https://pypi.org/project/preqs)
[![PyPI - Status](https://img.shields.io/pypi/status/preqs?style=flat-square)](https://pypi.org/project/preqs)
[![Static Badge](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](https://pypi.org/project/preqs)
[![Static Badge](https://img.shields.io/badge/code_coverage-100%25-brightgreen?style=flat-square)](https://pypi.org/project/preqs)
[![Static Badge](https://img.shields.io/badge/pylint_analysis-100%25-brightgreen?style=flat-square)](https://pypi.org/project/preqs)
[![PyPI - License](https://img.shields.io/pypi/l/preqs?style=flat-square)](https://opensource.org/license/gpl-3-0)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/preqs?style=flat-square)](https://pypi.org/project/preqs)

The `preqs` project is a cross-platform, simple, fast and easy-to-use requirements file generator. Your project's imported dependencies are collected into a `requirements.txt` file. No more, no less.


## Installation
Installing `preqs` is quick and easy. As a design feature, the library does not have any external (non-built-in) dependencies.
```
pip install preqs
```

## Usage
The help (or usage) menu can be displayed, as below, using the following command from the terminal:
```
preqs --help
```
Which displays:
```
usage: preqs [PATH] [options]

A simple (and fast) requirements.txt file generator.

positional arguments:
  PATH                  Path to the project's root directory.
                        Alternatively, the path where the search for modules should start.
                        Defaults to the current directory.

options:
  -c, --check           Perform requirements.txt file version checks against the installed
                        libraries, then exit.
  -d, --debug           Print verbose debugging output while processing.
  -i IGNORE_DIRS [IGNORE_DIRS ...], --ignore_dirs IGNORE_DIRS [IGNORE_DIRS ...]
                        One or more director(y|ies) to be ignored when collecting module files.
  -p, --print           Print the detected requirements, rather than creating a file.
  -r, --replace         Replace the current requirements.txt file.
                        
  -h, --help            Display this help and usage, then exit.
  -v, --version         Display the version and exit.

Copyright (C) 2024-2025 | 73rd Street Development
This program comes with ABSOLUTELY NO WARRANTY. This is free 
software; you can redistribute it and/or modify it under the terms 
of the GNU General Public License as published by the Free Software
Foundation.  A copy of the license is included with this 
package.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

preqs <installed version>
```


## Usage Example
In its simplest form, `preqs` can be run by just calling the program from within your project's root directory, without any arguments. The path from which the Python module discovery begins defaults to the *current directory*. If your project is in another directory, pass that directory's path into the `PATH` argument. The requirements file is saved into the path provided. 

**Notes:** 
- The following examples assume you are already in your project's root directory, therefore `PATH` is not provided.
- Any of the following flags may be combined to form your own requirements cocktail.

### Case 1: Simplest form
Simply generate a requirements file for your project, as:

1. Run `preqs` as:
```bash
preqs
``` 
2. Check the current directory for a `requirements.txt` file containing the project's external dependencies.

### Case 2: Ignoring directories
If you wish to exclude a directory (or directories) from the requirements file, the `--ignore_dirs` flag may be used as:

1. Run `preqs` as:
```bash
preqs --ignore_dirs docs build
```
2. Check the current directory for a `requirements.txt` file containing the project's external dependencies.

### Case 3: Display only (do not generate a file)
In some cases, for example with an existing requirements file you do not want to overwrite, you may wish to *display* the requirements to the terminal. This can be accomplished using the `--print` flag, as:

1. Run `preqs` as:
```bash
preqs --print
```
2. Watch the terminal for an output displaying the project's requirements.

### Case 4: Overwrite an existing requirements file
By default, if a `requirements.txt` file exists, you will be alerted. The existing file will *not* be overwritten. That is, unless you tell `preqs` it's OK.

1. Run `preqs` as:
```bash
preqs --replace
```
2. Check the current directory for a *new* `requirements.txt` file containing the project's external dependencies.

### Case 5: Check a requirements file against the installed libraries
The `--check` argument can be used to perform a version check between a requirements file and the installed libraries.

1. If  `preqs` is run as follows, the `requirements.txt` file in the current directory is used:
```bash
preqs --check
```

Alternatively, the path to *any* requirements file can be specified in the path as:
```bash
preqs ~/Desktop/requirements.txt --check
```

This will output a report similar to the following, showing the status of each requirements file entry relative to the installed libraries:
```
Name                     Requirement    Installed      Status
-----------------------------------------------------------------
beautifulsoup4           4.13.4         n/a            Not installed
colorama                 0.4.6          n/a            Not installed
ipython                  8.31.0         8.30.0         Older
spyder-kernels           3.0.1          3.0.2          Newer
jupyter_client           8.6.3          8.6.3          Same
requests                 2.32.3         n/a            Not installed
```


## Additional information

### How is the version number obtained?
The version number you see in the requirements file output is obtained using the built-in `importlib` library. Therefore, the package *must be installed* in the environment being used to run `preqs`.

- By design, we do *not* use PyPI to obtain version numbers as this practice usually involves assuming the latest version - whereas this may not be the case for your project.
- Any packages which are known to be imported by the project, and yet do not appear in the requirements file, *are likely not installed* in the environment. Run `preqs` with the `--print` flag to observe any packages which are imported for which the version number could not be obtained. These 'unknown version' packages are (currently) ignored when the requirements file is written.

### I don't see a specific package in the requirements file.
Refer to the *How is the version number obtained?* question.

### Why should I not just use `pip freeze`?
Many online 'tutorials' for generating a requirements file say to use `pip freeze` and redirect the output to a file called `requirements.txt`. However, this is not good practice for the following reasons:

- *All* of the packages installed in your development environment will be listed in the requirements file. This may include some (or many) packages which your project does not require, thus bloating the end-user's installation and thereby cluttering their environment. Or, the packages you have in your environment, although not used by the project, may be out-of-date; causing the end-user to be forced to install out-of-date packages.
- A true requirements file should contain *only* those packages which are imported and required by the project.
- Only the packages that were installed with `pip install` will be included in the requirements file.

