import pytest
from app import app
import os
import io
import tempfile
import shutil


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_upload_folder():
    temp_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_upload_files_no_files(client):
    response = client.post('/api/fs/upload', data={})
    assert response.status_code == 400
    assert response.json == {"error": "No files part"}


def test_get_file_info_invalid_identifier(client):
    response = client.get('/api/fs/info/invalididentifier')
    assert response.status_code == 404
    assert response.json == {"error": "Invalid or non-existent file identifier."}


def test_download_files_invalid_identifier(client):
    response = client.get('/api/fs/download/invalididentifier')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid identifier format"}


def test_get_statistics_error(client, mocker):
    mocker.patch('db.Connector.get_statistics', side_effect=Exception('DB error'))
    response = client.get('/api/fs/statistics')
    assert response.status_code == 500
    assert response.json == {"error": "DB error"}


def test_upload_and_cleanup_files(client, temp_upload_folder, mocker):
    files = [io.BytesIO(b"sample content")]
    files[0].name = 'test.txt'

    data = {
        'files': (files[0], 'test.txt')
    }

    mocker.patch('logic.Connector.insert_new_upload_db')
    mocker.patch('logic.Connector.update_statistics')

    response = client.post('/api/fs/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    result = response.json
    assert "link" in result

    identifier = result["link"].split('/')[-1]
    folder_path = os.path.join(temp_upload_folder, identifier)

    assert os.path.exists(folder_path)
    assert os.path.exists(os.path.join(folder_path, 'test.txt'))

    # Cleanup after the test
    shutil.rmtree(folder_path)
    assert not os.path.exists(folder_path)
