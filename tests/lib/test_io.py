# pylint: disable=missing-function-docstring disable=missing-module-docstring

import os
import shutil
import subprocess
from pathlib import Path

import pytest

import nestor_api.lib.io as io
from nestor_api.config.config import Configuration


def test_copy_single_file():
    fixtures_directory_path = Path(
        os.path.dirname(__file__), '..', '__fixtures__', 'example.yaml'
    ).resolve()
    destination_path = Path(
        os.path.dirname(__file__), '..', '__fixtures__', 'example_copy.yaml'
    ).resolve()

    io.copy(fixtures_directory_path, destination_path)

    assert os.path.isfile(destination_path)

    os.remove(destination_path)


def test_copy_directory_with_content():
    fixtures_directory_path = Path(os.path.dirname(__file__), '..', '__fixtures__').resolve()
    destination_path = Path(os.path.dirname(__file__), '..', '__fixtures__copy').resolve()
    fixtures_files = os.listdir(fixtures_directory_path)

    io.copy(fixtures_directory_path, destination_path)

    copied_fixtures_files = os.listdir(destination_path)

    assert os.path.isdir(destination_path)
    assert fixtures_files == copied_fixtures_files

    shutil.rmtree(destination_path)


def test_copy_should_raise_if_failure():
    with pytest.raises(Exception):
        fixtures_directory_path = Path(os.path.dirname(__file__), '..', '__abcdefg').resolve()
        destination_path = Path(os.path.dirname(__file__), '..', '__abcdefg_copy').resolve()

        io.copy(fixtures_directory_path, destination_path)


def test_create_temporary_directory():
    temporary_path = io.create_temporary_directory("prefix")

    assert temporary_path.startswith('/tmp/nestor/work/prefix-')
    assert os.path.isdir(temporary_path)

    shutil.rmtree(temporary_path)


def test_ensure_dir_existing_folder():
    # "tests" directory of the project
    tests_directory_path = Path(os.path.dirname(__file__), '..').resolve()

    io.ensure_dir(tests_directory_path)

    assert os.path.isdir(tests_directory_path)


def test_ensure_dir_not_existing_folder():
    # "tests/ensure_dir" directory in the project
    tests_directory_path = Path(os.path.dirname(__file__), '..', 'ensure_dir').resolve()

    assert not os.path.isdir(tests_directory_path)

    io.ensure_dir(tests_directory_path)

    assert os.path.isdir(tests_directory_path)

    os.rmdir(tests_directory_path)


def test_execute(mocker):
    mocker.patch.object(subprocess, 'run')

    io.execute('a command with --arg1 arg-value')

    subprocess.run.assert_called_with(
        ['a', 'command', 'with', '--arg1', 'arg-value'],
        check=True,
        cwd=None,
        stdout=-1
    )


def test_execute_should_raise_if_failure():
    with pytest.raises(Exception):
        io.execute('a command with --arg1 arg-value')


def test_exists_existing_file():
    existing_path = Path(os.path.dirname(__file__), "__init__.py").resolve()
    assert io.exists(existing_path)


def test_exists_not_existing_file():
    existing_path = Path(os.path.dirname(__file__), "abcdefghijklmnopqrstuvwxyz.py").resolve()
    assert not io.exists(existing_path)


def test_from_yaml():
    yaml_fixture_path = Path(
        os.path.dirname(__file__), "..", "__fixtures__", "example.yaml"
    ).resolve()

    parsed_yaml = io.from_yaml(yaml_fixture_path)

    assert parsed_yaml == {
        "name": "Martin D'vloper",
        "job": "Developer",
        "skill": "Elite",
        "employed": True,
        "foods": ["Apple", "Orange", "Strawberry", "Mango"],
        "languages": {"perl": "Elite", "python": "Elite", "pascal": "Lame"}
    }


def test_get_pristine_path_default():
    pristine_path = io.get_pristine_path("my_path_name")
    assert pristine_path == "/tmp/nestor/pristine/my_path_name"


def test_get_pristine_path_configured(mocker):
    mocker.patch.object(Configuration, "get_pristine_path", return_value="/tmp/a_configured_path")

    pristine_path = io.get_pristine_path("my_path_name")

    assert pristine_path == "/tmp/a_configured_path/my_path_name"


def test_get_temporary_copy():
    fixtures_directory_path = Path(os.path.dirname(__file__), '..', '__fixtures__').resolve()
    fixtures_files = os.listdir(fixtures_directory_path)

    temporary_directory_path = io.get_temporary_copy(fixtures_directory_path, 'my-application')

    copied_files = os.listdir(temporary_directory_path)

    assert temporary_directory_path.startswith('/tmp/nestor/work/my-application-')
    assert os.path.isdir(temporary_directory_path)
    assert fixtures_files == copied_files

    shutil.rmtree(temporary_directory_path)


def test_get_temporary_directory_path():
    generated_path = io.get_temporary_directory_path('test-prefix')

    assert generated_path.startswith('/tmp/nestor/work/test-prefix-')


def test_get_working_path_default():
    pristine_path = io.get_working_path("my_path_name")
    assert pristine_path == "/tmp/nestor/work/my_path_name"


def test_get_working_path_configured(mocker):
    mocker.patch.object(Configuration, "get_working_path", return_value="/tmp/a_configured_path")

    pristine_path = io.get_working_path("my_path_name")

    assert pristine_path == "/tmp/a_configured_path/my_path_name"


def test_remove_single_file():
    fixtures_directory_path = Path(
        os.path.dirname(__file__), '..', '__fixtures__', 'example.yaml'
    ).resolve()
    destination_path = Path(
        os.path.dirname(__file__), '..', '__fixtures__', 'example_copy.yaml'
    ).resolve()

    shutil.copyfile(fixtures_directory_path, destination_path)

    assert os.path.isfile(destination_path)

    io.remove(destination_path)

    assert not os.path.isfile(destination_path)


def test_remove_directory_with_content():
    fixtures_directory_path = Path(os.path.dirname(__file__), '..', '__fixtures__').resolve()
    destination_path = Path(os.path.dirname(__file__), '..', '__fixtures__copy').resolve()

    shutil.copytree(fixtures_directory_path, destination_path)

    assert os.path.isdir(destination_path)

    io.remove(destination_path)

    assert not os.path.isdir(destination_path)


def test_remove_should_raise_if_failure():
    with pytest.raises(Exception):
        not_existing_path = Path(os.path.dirname(__file__), '..', '__abcdefg').resolve()

        io.remove(not_existing_path)
