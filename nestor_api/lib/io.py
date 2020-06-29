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


def copy(source, destination):
    """Copy file or directory with its content from source to destination"""
    try:
        shutil.copytree(source, destination)
    except OSError as err:
        if err.errno == errno.ENOTDIR:
            shutil.copy(source, destination)
        else:
            raise


def create_temporary_directory(directory_prefix=""):
    """Creates a temporary directory with an optional prefix"""
    tmp_directory_path = get_temporary_directory_path(directory_prefix)

    # Create directory if it does not exist
    ensure_dir(tmp_directory_path)

    return tmp_directory_path


def ensure_dir(directory_path):
    """Ensures that a directory exists, else creates it"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def execute(command: str, cwd=None):
    """Executes a command and returns the stdout from it"""
    result = subprocess.run(command.split(), stdout=subprocess.PIPE, check=True, cwd=cwd)
    return result.stdout.decode("utf-8")


def exists(file_path):
    """Checks if a file exists"""
    return Path(file_path).exists()


def from_yaml(file_path):
    """Returns a dictionary from yaml file path"""
    with open(file_path, "r") as file_data:
        yaml_data = file_data.read()

    return yaml.safe_load(yaml_data)


def get_pristine_path(pristine_path_name):
    """Returns the pristine path"""
    return os.path.join(Configuration.get_pristine_path(), pristine_path_name)


def get_temporary_copy(directory_path, target_directory_prefix=""):
    """Creates a copy of a directory in a temporary directory and returns its path"""
    copy_path = get_temporary_directory_path(target_directory_prefix)
    copy(directory_path, copy_path)

    return copy_path


def get_temporary_directory_path(prefix=""):
    """Returns a temporary directory path with an optional prefix"""
    random_num = math.floor(random() * 1e9)
    random_str = "{:09d}".format(random_num)
    current_timestamp = str(datetime.now().timestamp()).replace(".", "")

    tmp_directory_name = f"{current_timestamp}-{random_str}"
    if len(prefix) > 0:
        tmp_directory_name = f"{prefix}-{tmp_directory_name}"

    return get_working_path(tmp_directory_name)


def get_working_path(working_path_name):
    """Returns the working path"""
    return os.path.join(Configuration.get_working_path(), working_path_name)


def remove(file_path):
    """Remove a file or a directory with its content"""
    try:
        shutil.rmtree(file_path)
    except OSError as err:
        if err.errno == errno.ENOTDIR:
            os.remove(file_path)
        else:
            raise
