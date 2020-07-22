"""I/O library"""
from datetime import datetime
import errno
import math
import os
from pathlib import Path
from random import random
import shutil
import subprocess

import yaml

from nestor_api.config.config import Configuration


def convert_to_yaml(data: dict) -> str:
    """Converts a dictionary into a valid yaml string"""
    return yaml.safe_dump(data)


def copy(source: str, destination: str) -> None:
    """Copy file or directory with its content from source to destination"""
    try:
        shutil.copytree(source, destination)
    except OSError as err:
        if err.errno == errno.ENOTDIR:
            shutil.copy(source, destination)
        else:
            raise


def create_temporary_directory(directory_prefix: str = "") -> str:
    """Creates a temporary directory with an optional prefix"""
    tmp_directory_path = get_temporary_directory_path(directory_prefix)

    # Create directory if it does not exist
    ensure_dir(tmp_directory_path)

    return tmp_directory_path


def ensure_dir(directory_path: str) -> None:
    """Ensures that a directory exists, else creates it"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def execute(command: str, cwd: str = None, env: dict = None) -> str:
    """Executes a command and returns the stdout from it"""
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=env,
        shell=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8").rstrip()
        raise RuntimeError(stderr)

    return result.stdout.decode("utf-8").rstrip()


def exists(file_path: str) -> bool:
    """Checks if a file exists"""
    return Path(file_path).exists()


def get_pristine_path(pristine_path_name: str) -> str:
    """Returns the pristine path"""
    return os.path.join(Configuration.get_pristine_path(), pristine_path_name)


def create_temporary_copy(directory_path: str, target_directory_prefix: str = "") -> str:
    """Creates a copy of a directory in a temporary directory and returns its path"""
    copy_path = get_temporary_directory_path(target_directory_prefix)
    copy(directory_path, copy_path)

    return copy_path


def get_temporary_directory_path(prefix: str = "") -> str:
    """Returns a temporary directory path with an optional prefix"""
    random_num = math.floor(random() * 1e9)
    random_str = "{:09d}".format(random_num)
    current_timestamp = str(datetime.now().timestamp()).replace(".", "")

    tmp_directory_name = f"{current_timestamp}-{random_str}"
    if len(prefix) > 0:
        tmp_directory_name = f"{prefix}-{tmp_directory_name}"

    return get_working_path(tmp_directory_name)


def get_working_path(working_path_name: str) -> str:
    """Returns the working path"""
    return os.path.join(Configuration.get_working_path(), working_path_name)


def read(file_path: str) -> str:
    """Read the file content at the given path"""
    with open(file_path, "r") as file:
        file_content = file.read()
    return file_content


def remove(file_path: str) -> None:
    """Remove a file or a directory with its content"""
    try:
        shutil.rmtree(file_path)
    except OSError as err:
        if err.errno == errno.ENOTDIR:
            os.remove(file_path)
        else:
            raise


def write(file_path: str, content: str) -> None:
    """ Write the string content into the file at the given path"""
    with open(file_path, "w") as file:
        file.write(content)
