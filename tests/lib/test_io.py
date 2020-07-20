import errno
import filecmp
import os
from pathlib import Path
import subprocess
from tempfile import gettempdir
from unittest import TestCase
from unittest.mock import mock_open, patch

import nestor_api.lib.io as io


class TestIoLib(TestCase):
    def test_convert_to_yaml(self):
        dictionary_to_convert = {
            "name": "John Doe",
            "contact": {"phone": 1234567890, "mail": "john@doe.com"},
            "items": ["items1", "items2"],
        }

        yaml = io.convert_to_yaml(dictionary_to_convert)

        self.assertEqual(
            yaml,
            "contact:\n  mail: john@doe.com\n  phone: 1234567890\nitems:\n- "
            "items1\n- items2\nname: John Doe\n",
        )

    @patch("nestor_api.lib.io.shutil", autospec=True)
    def test_copy_single_file(self, shutil_mock):
        shutil_mock.copytree.side_effect = OSError(errno.ENOTDIR, "some reason")
        io.copy("source/path/file.yaml", "dest/path/file.yaml")
        shutil_mock.copytree.assert_called_once()
        shutil_mock.copy.assert_called_with("source/path/file.yaml", "dest/path/file.yaml")

    @patch("nestor_api.lib.io.shutil", autospec=True)
    def test_copy_directory_with_content(self, shutil_mock):
        io.copy("source/path/", "dest/path/")
        shutil_mock.copytree.assert_called_once()
        shutil_mock.copy.assert_not_called()

    @patch("nestor_api.lib.io.shutil", autospec=True)
    def test_copy_should_raise_if_failure(self, shutil_mock):
        exception = OSError()
        shutil_mock.copytree.side_effect = exception
        with self.assertRaises(OSError) as context:
            io.copy("source/path/", "dest/path/")
        self.assertEqual(exception, context.exception)
        shutil_mock.copy.assert_not_called()

    @patch("nestor_api.lib.io.get_temporary_directory_path", autospec=True)
    @patch("nestor_api.lib.io.ensure_dir", autospec=True)
    def test_create_temporary_directory(self, ensure_dir_mock, get_temporary_directory_path_mock):
        get_temporary_directory_path_mock.return_value = "path/to/temporary/prefix-dir"

        temporary_path = io.create_temporary_directory("prefix")

        get_temporary_directory_path_mock.assert_called_with("prefix")
        ensure_dir_mock.assert_called_with("path/to/temporary/prefix-dir")
        self.assertEqual(temporary_path, "path/to/temporary/prefix-dir")

    @patch("nestor_api.lib.io.Path", autospec=True)
    def test_ensure_dir(self, path_mock):
        io.ensure_dir("path/to/test")
        path_mock.return_value.mkdir.assert_called_with(parents=True, exist_ok=True)

    @patch("nestor_api.lib.io.subprocess.run", autospec=True)
    def test_execute(self, subprocess_run_mock):
        subprocess_run_mock.return_value.stdout.decode.return_value = "some output\n"

        output = io.execute("a command with --arg1 arg-value")

        self.assertEqual(output, "some output")
        subprocess_run_mock.assert_called_with(
            ["a", "command", "with", "--arg1", "arg-value"],
            check=True,
            cwd=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

    @patch("nestor_api.lib.io.subprocess.run", autospec=True)
    def test_execute_should_raise_if_failure(self, subprocess_run_mock):
        exception = Exception("some exception")
        subprocess_run_mock.side_effect = exception
        with self.assertRaises(Exception) as context:
            io.execute("a command with --arg1 arg-value")
        self.assertEqual(exception, context.exception)

    @patch("nestor_api.lib.io.Path", autospec=True)
    def test_exists_existing_file(self, path_mock):
        path_mock.return_value.exists.return_value = True
        result = io.exists("existing/path")
        path_mock.assert_called_once_with("existing/path")
        path_mock.return_value.exists.assert_called_once()
        self.assertTrue(result)

    @patch("nestor_api.lib.io.Path", autospec=True)
    def test_exists_not_existing_file(self, path_mock):
        path_mock.return_value.exists.return_value = False
        result = io.exists("unexisting/path")
        path_mock.assert_called_once_with("unexisting/path")
        path_mock.return_value.exists.assert_called_once()
        self.assertFalse(result)

    @patch("nestor_api.lib.io.Configuration", autospec=True)
    def test_get_pristine_path(self, configuration_mock):
        configuration_mock.get_pristine_path.return_value = "/tmp/nestor/pristine"

        pristine_path = io.get_pristine_path("my_path_name")

        self.assertEqual(pristine_path, "/tmp/nestor/pristine/my_path_name")

    @patch("nestor_api.lib.io.get_temporary_directory_path", autospec=True)
    @patch("nestor_api.lib.io.copy", autospec=True)
    def test_create_temporary_copy(self, copy_mock, get_temporary_directory_path_mock):
        get_temporary_directory_path_mock.return_value = "/tmp/nestor/work/my-application-"

        temporary_directory_path = io.create_temporary_copy("some/path", "my-application")

        get_temporary_directory_path_mock.assert_called_with("my-application")
        copy_mock.assert_called_with("some/path", "/tmp/nestor/work/my-application-")
        self.assertEqual(temporary_directory_path, "/tmp/nestor/work/my-application-")

    @patch("nestor_api.lib.io.get_working_path", autospec=True)
    def test_get_temporary_directory_path(self, get_working_path_mock):
        get_working_path_mock.return_value = "/tmp/nestor/work/test-prefix-"
        generated_path = io.get_temporary_directory_path("test-prefix")

        tmp_directory_name = get_working_path_mock.call_args[0][0]
        self.assertTrue(tmp_directory_name.startswith("test-prefix-"))
        self.assertEqual(generated_path, "/tmp/nestor/work/test-prefix-")

    @patch("nestor_api.lib.io.Configuration", autospec=True)
    @patch("nestor_api.lib.io.os", autospec=True)
    def test_get_working_path(self, os_mock, configuration_mock):
        # Mocks
        configuration_mock.get_working_path.return_value = "/tmp/nestor/work/"
        os_mock.path.join.return_value = "/tmp/nestor/work/my_path_name"

        # Test
        working_path = io.get_working_path("my_path_name")

        # Assertions
        os_mock.path.join.assert_called_with("/tmp/nestor/work/", "my_path_name")
        self.assertEqual(working_path, "/tmp/nestor/work/my_path_name")

    def test_read(self):
        sample_file_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "io", "sample.txt"
        ).resolve()
        content = io.read(sample_file_path)
        self.assertEqual(content, "sample file\n")

    @patch("nestor_api.lib.io.yaml", autospec=True)
    def test_read_yaml(self, yaml_mock):
        with patch("nestor_api.lib.io.open", mock_open(read_data="key: value")) as open_mock:
            yaml_mock.safe_load.return_value = {"key": "value"}

            parsed_yaml = io.read_yaml("example.yml")

            open_mock.assert_called_with("example.yml", "r")
            yaml_mock.safe_load.assert_called_once_with("key: value")
            self.assertEqual(parsed_yaml, {"key": "value"})

    @patch("nestor_api.lib.io.os", autospec=True)
    @patch("nestor_api.lib.io.shutil", autospec=True)
    def test_remove_single_file(self, shutil_mock, os_mock):
        io.remove("path/to/remove")
        shutil_mock.rmtree.assert_called_once_with("path/to/remove")
        os_mock.remove.assert_not_called()

    @patch("nestor_api.lib.io.os", autospec=True)
    @patch("nestor_api.lib.io.shutil", autospec=True)
    def test_remove_directory_with_content(self, shutil_mock, os_mock):
        shutil_mock.rmtree.side_effect = OSError(errno.ENOTDIR, "some reason")
        io.remove("path/to/remove")
        shutil_mock.rmtree.assert_called_once_with("path/to/remove")
        os_mock.remove.assert_called_once_with("path/to/remove")

    @patch("nestor_api.lib.io.os", autospec=True)
    @patch("nestor_api.lib.io.shutil", autospec=True)
    def test_remove_should_raise_if_failure(self, shutil_mock, os_mock):
        exception = OSError()
        shutil_mock.rmtree.side_effect = exception

        with self.assertRaises(OSError) as context:
            io.remove("path/to/remove")
        self.assertEqual(exception, context.exception)
        shutil_mock.rmtree.assert_called_once_with("path/to/remove")
        os_mock.remove.assert_not_called()

    def test_write(self):
        temporary_file_path = os.path.join(gettempdir(), "test_write.txt")
        sample_file_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "io", "sample.txt"
        ).resolve()

        io.write(temporary_file_path, "sample file\n")
        self.assertTrue(filecmp.cmp(temporary_file_path, sample_file_path))

        os.remove(temporary_file_path)
