"""Workflow library utils."""

import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def non_blocking_clean(path):
    """Try to clean directory/file at path but don't
    raise an error if it fails (only log it)"""
    try:
        io.remove(path)
    except Exception as err:
        Logger.warn(
            {"path": path, "err": str(err)}, "Error trying to clean temporary directory/file"
        )
