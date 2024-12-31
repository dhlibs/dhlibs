# This file is part of dhlibs (https://github.com/DinhHuy2010/dhlibs)
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
# SPDX-License-Identifier: MIT OR Apache-2.0 OR MPL-2.0

"""dhlibs - random libraries that you shouldn't care"""


def _get_version():
    import importlib.metadata

    return importlib.metadata.version(__name__)


__author__ = "DinhHuy2010"
__copyright__ = "Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)"
__license__ = "MIT"
__version__ = _get_version()

del _get_version
