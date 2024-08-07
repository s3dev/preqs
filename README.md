![Static Badge](https://img.shields.io/badge/tests-passing-brightgreen) ![Static Badge](https://img.shields.io/badge/coverage-100%25-brightgreen)  ![Static Badge](https://img.shields.io/badge/pylint_analysis-100%25-brightgreen)

# A simple (and fast) requirements.txt file generator
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
  -d, --debug           Print verbose debugging output while processing.
  -i IGNORE_DIRS [IGNORE_DIRS ...], --ignore_dirs IGNORE_DIRS [IGNORE_DIRS ...]
                        One or more director(y|ies) to be ignored when collecting module files.
  -p, --print           Print the detected requirements, rather than creating a file.
  -r, --replace         Replace the current requirements.txt file.
                        
  -h, --help            Display this help and usage, then exit.
  -v, --version         Display the version and exit.

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

