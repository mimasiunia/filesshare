import pytest
import os
import shutil
import tempfile
from logic import save_files, get_folder_size, generate_identifier, validate_identifier, get_folder_path


@pytest.fixture
def temp_upload_folder():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_save_files(temp_upload_folder, mocker):
    file_content = b"sample content"
    files = [mocker.Mock()]
    files[0].filename = 'test.txt'
    files[0].save = mocker.Mock(side_effect=lambda filepath: open(filepath, 'wb').write(file_content))

    mocker.patch('logic.Connector.insert_new_upload_db')
    mocker.patch('logic.Connector.update_statistics')

    result = save_files(files, temp_upload_folder)

    # logging
    save_path = os.path.join(temp_upload_folder, result["identifier"])
    expected_file_path = os.path.join(save_path, 'test.txt')

    print(f"Expected file path: {expected_file_path}")
    print(f"Directory contents: {os.listdir(temp_upload_folder)}")
    if os.path.exists(save_path):
        print(f"Saved files: {os.listdir(save_path)}")

    assert result["error"] is None
    assert os.path.exists(expected_file_path), f"File not found: {expected_file_path}"
    with open(expected_file_path, 'rb') as f:
        assert f.read() == file_content
    files[0].save.assert_called_once()

    # Cleanup after the test
    shutil.rmtree(save_path)
    assert not os.path.exists(save_path)


def test_get_folder_size(temp_upload_folder):
    file_path = os.path.join(temp_upload_folder, 'test.txt')
    with open(file_path, 'w') as f:
        f.write('content')

    size_gb, file_count = get_folder_size(temp_upload_folder)

    assert file_count == 1
    assert size_gb > 0


def test_generate_identifier():
    identifier = generate_identifier()
    assert len(identifier) == 12
    assert identifier.isalnum()


def test_validate_identifier():
    assert validate_identifier('a1b2c3d4e5f6')
    assert not validate_identifier('short')
    assert not validate_identifier('invalid_identifier!')


def test_get_folder_path(temp_upload_folder):
    identifier = 'testfolder'
    os.mkdir(os.path.join(temp_upload_folder, identifier))

    folder_path = get_folder_path(identifier, temp_upload_folder)

    assert folder_path == os.path.join(temp_upload_folder, identifier)


def test_get_folder_path_non_existent(temp_upload_folder):
    folder_path = get_folder_path('nonexistent', temp_upload_folder)

    assert folder_path is None
