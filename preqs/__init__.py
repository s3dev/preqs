# Setup for relative imports
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
# locals
from ._version import __version__
