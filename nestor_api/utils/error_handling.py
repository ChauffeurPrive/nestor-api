"""Error handling utils."""

import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def non_blocking_clean(path: str, *, message_prefix: str = None):
    """Try to clean directory/file at path but don't
    raise an error if it fails (only log it)."""
    message = "Error trying to clean temporary directory / file"
    if message_prefix is not None:
        message = message_prefix.strip() + f" {message}"

    try:
        io.remove(path)
        # pylint: disable=broad-except
    except Exception as err:
        Logger.warn({"path": path, "err": str(err)}, message)
