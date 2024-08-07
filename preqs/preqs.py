#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:App:       preqs
:Purpose:   The preqs project is a simple (and fast) requirements.txt
            file generator.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Note:      Per ``logging`` documentation, the logging functions
            [are optimised](https://docs.python.org/3/howto/logging.html#optimization)
            to use lazy % string formatting rather than f-strings.
            This is not a relic and should remain in tact as long as
            the logging documentation specifies this.

"""
# pylint: disable=import-error

import argparse
import ast
import os
import hashlib
import logging
import sys
import traceback
from datetime import datetime as dt
from enum import Enum
from glob import glob
from importlib import metadata
# locals
try:
    from _version import __version__
except ImportError:
    from ._version import __version__


class ArgParser:
    """Command line argument parsing class for the project."""

    # Program usage and help strings.
    _proj = 'preqs'
    _vers = __version__
    _desc = 'A simple (and fast) requirements.txt file generator.'
    _usag = 'preqs [PATH] [options]'
    _h_dbug = 'Print verbose debugging output while processing.'
    _h_dirs = 'One or more director(y|ies) to be ignored when collecting module files.'
    _h_path = ('Path to the project\'s root directory.\n'
               'Alternatively, the path where the search for modules should start.\n'
               'Defaults to the current directory.')
    _h_prnt = 'Print the detected requirements, rather than creating a file.'
    _h_repl = 'Replace the current requirements.txt file.\n\n'
    _h_vers = 'Display the version and exit.'
    _h_help = 'Display this help and usage, then exit.'

    def __init__(self):
        """Argument parser class initialiser."""
        self._args = None
        self._epil = self._build_epilog()

    @property
    def args(self):
        """Accessor to parsed arguments."""
        return self._args

    def parse(self):
        """Parse command line arguments."""
        # pylint: disable=line-too-long
        argp = argparse.ArgumentParser(prog=self._proj,
                                       usage=self._usag,
                                       description=self._desc,
                                       epilog=self._epil,
                                       formatter_class=argparse.RawTextHelpFormatter,
                                       add_help=False)
        # Order matters here as it affects the display -->
        argp.add_argument('PATH', help=self._h_path, nargs='?', default=os.getcwd())
        argp.add_argument('-d', '--debug', help=self._h_dbug, action='store_true')
        argp.add_argument('-i', '--ignore_dirs', help=self._h_dirs, nargs='+')
        argp.add_argument('-p', '--print', help=self._h_prnt, action='store_true')
        argp.add_argument('-r', '--replace', help=self._h_repl, action='store_true')
        argp.add_argument('-h', '--help', help=self._h_help, action='help')
        argp.add_argument('-v', '--version', help=self._h_vers, action='version', version=self._epil)
        self._args = argp.parse_args()

    def _build_epilog(self) -> str:
        """Build the epilog string for terminal display.

        Returns:
            str: A string containing the text to be displayed in the
            epilog of the help menu.

        """
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'NOTICE')
        with open(path, 'r', encoding='utf-8') as f:
            notice = f.read()
        epil = f'{notice}\n\n{self._proj} v{self._vers}'
        return epil


class CodeParser:
    """The internal Python module code parser.

    This code parser uses `ast` to parse a Python module and extract any
    import statements, whose module name is returned to the caller.

    Note:
        ``classmethod`` decorators are used here so the class can be
        used within the need for instantiation.

    """

    @classmethod
    def extract_imports(cls, path: str) -> set:
        """Extract imported modules from the provided Python module.

        Args:
            path (str): Path to the Python module to be analysed.

        Returns:
            set: A set containing the imported modules.

        """
        nodes = cls._ast_parse(path=path)
        imports = cls._read_nodes(nodes=nodes)
        return imports

    @classmethod
    def _ast_parse(cls, path: str) -> filter:
        """Parse the Python module using ``ast``.

        Args:
            path (str): Path to the Python module to be analysed.

        Returns:
            filter: A filter object containing the ``ast`` nodes matching
            an instance of ``ast.Import`` or ``ast.ImportFrom``.

        """
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        nodes = filter(lambda x: isinstance(x, (ast.Import, ast.ImportFrom)),
                       ast.walk(ast.parse(code)))
        return nodes

    @classmethod
    def _read_nodes(cls, nodes: filter) -> set:
        """Extract the module name from the provided nodes.

        Args:
            nodes (filter): The ``nodes`` object is expected to be
                provided using the :meth:`_ast_parse` method of this
                class.

        Returns:
            set: A set containing the module names imported in the parsed
            Python module.

        """
        imports = set()
        for node in nodes:
            if isinstance(node, ast.Import):
                imports.update((n.name for n in node.names))
            if isinstance(node, ast.ImportFrom) and not node.level:
                imports.add(node.module)
        return imports


class ExCode(Enum):
    """Exit code enumerators."""

    GEN_OK = 0
    ERR_EXIST = 10
    ERR_FILES = 20
    ERR_IMPTS = 30
    ERR_CLEAN = 40
    ERR_VERSN = 50
    ERR_WRITE = 60
    ERR_INITL = 255


class Requirements:
    """Python project requirements capture class.

    Once the ``import`` statements have been extracted from each Python
    module (defined by the :attr:`_FILE_EXTS` constant) in the project,
    the version for each imported package is looked up and reported in
    a ``requirements.txt`` file, or simply displayed in the terminal if
    the ``--print`` argument is provided.

    """

    _FILE_EXTS = ['*.py', '*.pyw']
    _IGNORE_DIRS = list(map(os.path.realpath, [
                                               '.ipynb_checkpoints',
                                               '.git',
                                               '.svn',
                                               '.tox',
                                               'test',
                                               'tests',
                                               '__pycache__',
                                              ]))

    def __init__(self):
        """Requirements class initialiser."""
        self._args = None
        self._excode = ExCode.ERR_INITL # Initial exit code value.
        self._files = None              # Set of Python modules to be analysed.
        self._imps = set()              # Set of discovered imported modules.
        self._reqs = set()              # Set of requirements to be written.
        self._ofile = None              # Full path to the output file.
        self._setup_parse_arguments()
        self._setup_logger()

    def run(self):
        """Program entry-point and requirements generator.

        This method operates using 'running boolean' logic, whereby each
        step is only executed if the previous step succeeds. Any step
        which fails, falls through to the end of the method with the
        associated exit status.

        """
        # pylint: disable=multiple-statements
        try:
            s = self._file_not_exists()
            if s: self._startup_msgs()
            if s: s = self._find_files()
            if s: s = self._collect_imports()
            if s: s = self._clean_imports()
            if s: s = self._get_installed_version()
            if s: s = self._write()
            self._shutdown_msgs()
        except Exception:  # pragma: nocover
            print()
            logging.critical('The following error occurred:\n\n%s\nProcessing aborted.\n',
                             traceback.format_exc())
        sys.exit(self._excode.value)

    def _clean_imports(self) -> bool:
        """Remove any local packages and builtins from the imports.

        Returns:
            bool: True if all local packages and builtins have been
            removed, otherwise False with the associated exit code being
            set.

        """
        _locals = self._define_locals(files=self._files)
        _builtins = sys.stdlib_module_names
        self._imps = self._imps - _builtins - (self._imps & _locals)
        # Verify all locals and builtins have been removed.
        if self._imps & _locals & _builtins:  # pragma: nocover
            self._excode = ExCode.ERR_CLEAN
            return False
        return True

    def _collect_imports(self) -> bool:
        """For each module found, extract the import statements.

        Returns:
            bool: True the :attr:`_imps` (imports) attribute is
            populated at the end, otherwise False with the associated
            exit code being set.

        """
        logging.debug('Starting import statement extraction on %d files ...', len(self._files))
        for f in self._files:
            logging.debug('Reading file: %s', os.path.basename(f))
            imports = CodeParser.extract_imports(path=f)
            logging.debug('- Found imports: %s', imports if imports else None)
            if imports:
                self._imps = self._imps.union(imports)
        # Set an import as 'spam' rather than 'spam.eggs'
        self._imps = set(i.partition('.')[0] for i in self._imps)
        if not self._imps:
            self._excode = ExCode.ERR_IMPTS
            return False
        return True

    def _compare(self, content: str) -> bool:
        """Compare the requirements file content to the expected hash.

        Args:
            content (str): String which was written to the requirements
                file.

        Returns:
            bool: True if the hash of the requirements string matches
            the requirements file itself.

        """
        shash = hashlib.md5(content.encode()).hexdigest()
        with open(self._ofile, 'rb') as f:
            text = f.read()
        fhash = hashlib.md5(text).hexdigest()
        return shash == fhash

    @staticmethod
    def _define_locals(files: list) -> set:
        """Create a set of modules which are local to the project.

        Any modules which are local, are to be removed from the imports
        list as these are not *external* packages to be included in the
        requirements file.

        Args:
            files (list): List of explicit file paths to this project's
                Python modules.

        Returns:
            set: A set of modules which are local to this project, which
            are to be removed from the requirements file.

        """
        parts = set()
        # Parse the file paths into their parts.
        parts.update(*map(lambda x: tuple(os.path.normpath(x).split(os.sep)), files))
        # Add parts (also) without file extensions.
        parts.update(map(lambda x: os.path.splitext(x)[0], parts.copy()))
        parts = parts - {'', '.', '..'}
        return parts

    def _file_not_exists(self) -> bool:
        """Test if a requirements file already exists at the path.

        Additionally, this method sets the path of the output file, to
        the :attr:`_ofile` attribute.

        Returns:
            bool: True if *either* a requirements file does not exist at
            the provided ``PATH``, the ``--replace`` argument is True,
            or the ``--print`` argument is True. Otherwise, False.

        """
        self._ofile = os.path.join(self._args.PATH, 'requirements.txt')
        if not os.path.exists(self._ofile) or self._args.replace or self._args.print:
            return True
        msg = ('The following path already exists, aborting:\n'
               '- %s'
               '\n\n'
               'Alternatively, pass the --replace flag to ignore this message and replace\n'
               'the existing file.\n')
        print()
        logging.warning(msg, self._ofile)
        self._excode = ExCode.ERR_EXIST
        return False

    def _find_files(self) -> bool:
        """Collect all Python module files.

        Set the internal :attr:`_files` attribute to a list of files with
        the defined file extension(s), except those files contained in
        any of the :attr:`_IGNORE_DIRS` directories.

        Note:
            Hidden files are only detected for Python versions 3.11+.

        Returns:
            bool: True if the list of files is populated, otherwise
            False with the associates exit code being set.

        """
        logging.debug('Starting module file collection ...')
        files = set()
        tmp = []
        for ext in self._FILE_EXTS:
            vmaj, vmin = sys.version_info[:2]
            # Hidden files are only available for Python 3.11+ due to glob limitations.
            if all((vmaj >= 3, vmin >= 11)):
                tmp.extend(glob(os.path.join(self._args.PATH, '**', ext),
                                recursive=True,
                                include_hidden=True))
            else:  # pragma: nocover
                tmp.extend(glob(os.path.join(self._args.PATH, '**', ext), recursive=True))
        # Only keep files which are not in an ignored directory.
        for file_ in tmp:
            if all((dir_ not in file_ for dir_ in self._IGNORE_DIRS)):
                files.add(file_)
        if self._args.debug:
            logging.debug('Module files found: %s',
                          ''.join(map('\n\t - {}'.format, files)))
        self._files = files
        if not self._files:
            self._excode = ExCode.ERR_FILES
            return False
        return True

    def _get_installed_version(self) -> bool:
        """Get the installed version for each package import.

        If a package is not installed or the version cannot be looked up,
        the ``importlib.metadata.PackageNotFoundError`` exception is
        handled and 'Unknown or not installed' is reported. However, this
        string is removed from the actual requirements file.

        Returns:
            bool: Always returns True.

        """
        for pkg in self._imps:
            try:
                self._reqs.add((pkg, metadata.version(pkg)))
            except metadata.PackageNotFoundError:
                self._reqs.add((pkg, 'Unknown or not installed'))
        return True

    def _setup_logger(self):
        """Setup: Set the project logger."""
        level = logging.DEBUG if self._args.debug else logging.INFO
        logging.basicConfig(level=level, format="[%(levelname)s]: %(message)s")

    def _setup_parse_arguments(self):
        """Setup: Parse the command line arguments.

        Additionally:

            - The ``PATH`` argument is updated to contain the explicit
              path (i.e. using ``realpath``).
            - The :attr:`_IGNORE_DIRS` attribute is updated with any
              directories passed as an argument.

        """
        ap = ArgParser()
        ap.parse()
        ap.args.PATH = os.path.realpath(ap.args.PATH)
        if ap.args.ignore_dirs:  # pragma: nocover (Cannot test; this is called on instantiation)
            self._IGNORE_DIRS += list(map(os.path.realpath, ap.args.ignore_dirs))
        self._args = ap.args

    def _shutdown_msgs(self):
        """Print any shutdown messages."""
        logging.debug('All imports being reported: %s', self._imps)
        logging.debug('All requirements being reported: %s', self._reqs)
        if self._excode == ExCode.GEN_OK:
            if not self._args.print:
                print()
                logging.info('The requirements file has been written here:\n- %s\n', self._ofile)
        elif self._excode == ExCode.ERR_FILES:
            print()
            logging.warning('No Python modules found in this project.\n')
        elif self._excode == ExCode.ERR_IMPTS:
            print()
            logging.warning('No imports found for this project.\n')
        elif self._excode != ExCode.ERR_EXIST:  # pragma: nocover
            logging.error('An error occurred while processing. Exit code: %d', self._excode.value)
            print()

    def _startup_msgs(self):
        """Print any startup messages."""
        logging.debug('Starting up ...')
        if self._args.debug:
            logging.debug('Ignoring the following directories: %s',
                          ''.join(map('\n\t - {}'.format, self._IGNORE_DIRS)))

    def _write(self) -> bool:
        """Write (or display) the requirements file.

        If the ``--print`` argument was passed, the requirements are
        displayed to the terminal. Otherwise, the requirements are
        written to the ``requirements.txt`` file at the ``PATH``
        provided.

        .. warning::

            This method will **replace** the existing ``requirements.txt``
            file.

            The test for file replacement is carried out on program
            start-up by the :meth:`_file_not_exists` method.

        Returns:
            bool: True if either the ``--print`` argument is True or
            if the file is written as expected (based on an MD5 hash
            checksum). Otherwise False, with the associated exit code
            being set.

        """
        _reqs = sorted(self._reqs)
        if self._args.print:
            print('\nThe following requirements were captured:',
                  '-'*42,
                  *_reqs,
                  '',
                  sep='\n')
        else:
            genby = f'# Generated by: preqs v{__version__} ({dt.now().astimezone().isoformat()})'
            content = ('\n'.join(f'{pkg}=={ver}'
                                 for pkg, ver in _reqs
                                 if 'Unknown' not in ver)
                       + f'\n\n{genby}\n')
            with open(self._ofile, 'w', encoding='utf-8') as f:
                f.write(content)
            if not self._compare(content=content):  # pragma: nocover
                self._excode = ExCode.ERR_WRITE
                return False
        self._excode = ExCode.GEN_OK  # Indicate successful completion.
        return True


#%%

# Prevent from running on module import.

# Enable running as either a script (dev/debugging) or as an executable.
if __name__ == '__main__':  # pragma: nocover
    r = Requirements()
    r.run()
else:  # pragma: nocover
    def main():
        """Entry-point exposed for the executable.

        The ``"preqs.preqs:main"`` value is set in ``pyproject.toml``'s
        ``[project.scripts]`` table as the entry-point for the installed
        executable.

        """
        # pylint: disable=redefined-outer-name
        r = Requirements()
        r.run()
