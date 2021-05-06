# -*- coding: utf-8 -*-

"""Top-level package for Text Diff."""

__author__ = "Rémi Delbouys"
__email__ = "remi.delbouys@laposte.net"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.2"


def get_module_version():
    return __version__


from .extract_diff import (  # noqa: F401
    AddedLine,
    DiffLine,
    EditOperation,
    Mask,
    ModifiedLine,
    RemovedLine,
    TextDifferences,
    UnchangedLine,
    text_differences,
)
